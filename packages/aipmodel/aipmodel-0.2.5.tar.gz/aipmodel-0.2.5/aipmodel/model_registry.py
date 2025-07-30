import os
import sys
import socket
import requests
import boto3
from huggingface_hub import snapshot_download
from tqdm import tqdm
from base64 import b64encode
from botocore.exceptions import ClientError, EndpointConnectionError


# ------------------------------
# Ceph S3 Manager
# ------------------------------
class CephS3Manager:
    def __init__(self, endpoint_url, access_key, secret_key, bucket_name):
        self.s3 = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        self.bucket_name = bucket_name

    def ensure_bucket_exists(self):
        try:
            buckets = self.s3.list_buckets()
            names = [b['Name'] for b in buckets.get('Buckets', [])]
            if self.bucket_name not in names:
                try:
                    self.s3.create_bucket(Bucket=self.bucket_name)
                    print(f"[OK] Ceph S3 Bucket Created: {self.bucket_name}")
                except ClientError as e:
                    if e.response['Error']['Code'] == "TooManyBuckets":
                        print(f"[WARN] Bucket limit reached. Please ensure bucket '{self.bucket_name}' exists.")
                    else:
                        raise e
            else:
                print(f"[OK] Ceph S3 Bucket Exists: {self.bucket_name}")
        except Exception as e:
            print(f"[FAIL] Ensure Bucket Error: {e}")

    def check_connection(self):
        try:
            self.s3.list_buckets()
            print("[OK] Ceph S3 Connection")
            return True
        except EndpointConnectionError:
            print("[FAIL] Ceph S3 Connection")
            return False
        except ClientError as e:
            print(f"[FAIL] Ceph S3 ClientError: {e.response['Error']['Code']}")
            return False
        except Exception:
            print("[FAIL] Ceph S3 Unknown")
            return False

    def check_auth(self):
        try:
            self.s3.list_buckets()
            print("[OK] Ceph S3 Auth")
            return True
        except ClientError as e:
            code = e.response['Error']['Code']
            if code in ["InvalidAccessKeyId", "SignatureDoesNotMatch"]:
                print("[FAIL] Ceph S3 Auth Invalid")
            else:
                print(f"[FAIL] Ceph S3 Auth: {code}")
            return False
        except Exception:
            print("[FAIL] Ceph S3 Auth Unknown")
            return False

    def check_if_exists(self, key):
        resp = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=key)
        return resp.get("Contents", []) if "Contents" in resp else None

    def is_folder(self, key):
        contents = self.check_if_exists(key)
        return bool(contents) and any(obj['Key'] != key for obj in contents)

    def download_file(self, remote_path, local_path):
        if os.path.isdir(local_path):
            local_path = os.path.join(local_path, os.path.basename(remote_path))
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        resp = self.s3.get_object(Bucket=self.bucket_name, Key=remote_path)
        with open(local_path, "wb") as f:
            f.write(resp["Body"].read())
        print(f"[Download] {remote_path} -> {local_path}")

    def download_folder(self, remote_folder, local_folder):
        if not remote_folder.endswith("/"):
            remote_folder += "/"
        resp = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=remote_folder)
        if "Contents" not in resp:
            print(f"[FAIL] Folder {remote_folder} not found")
            return
        with tqdm(total=len(resp["Contents"]), desc="Downloading") as pbar:
            for obj in resp["Contents"]:
                key = obj["Key"]
                rel_path = key[len(remote_folder):]
                local_file = os.path.join(local_folder, rel_path)
                self.download_file(key, local_file)
                pbar.update(1)

    def download(self, remote_path, local_path):
        if os.path.isfile(local_path) and self.is_folder(remote_path):
            raise ValueError("Cannot download folder to file path")
        if os.path.isdir(local_path) and not self.is_folder(remote_path):
            local_path = os.path.join(local_path, os.path.basename(remote_path))
        if self.is_folder(remote_path):
            self.download_folder(remote_path, local_path)
        else:
            self.download_file(remote_path, local_path)

    def upload_file(self, local_file_path, remote_path):
        self.s3.upload_file(local_file_path, self.bucket_name, remote_path)
        print(f"[Upload] {local_file_path} -> s3://{self.bucket_name}/{remote_path}")

    def upload(self, local_path, remote_path):
        if os.path.isfile(local_path) and self.is_folder(remote_path):
            raise ValueError("Cannot upload file to folder path")
        if os.path.isdir(local_path):
            if self.check_if_exists(remote_path) and not self.is_folder(remote_path):
                raise ValueError("Cannot upload folder to file path")
        if os.path.isdir(local_path):
            for root, _, files in os.walk(local_path):
                for file in files:
                    local_file = os.path.join(root, file)
                    s3_key = os.path.join(remote_path, os.path.relpath(local_file, local_path)).replace("\\", "/")
                    self.upload_file(local_file, s3_key)
        else:
            self.upload_file(local_path, remote_path)

    def delete_folder(self, prefix):
        objects = self.check_if_exists(prefix)
        if objects:
            for obj in objects:
                self.s3.delete_object(Bucket=self.bucket_name, Key=obj['Key'])
            print(f"[Delete] s3://{self.bucket_name}/{prefix}")


# ------------------------------
# Health Checker
# ------------------------------
class HealthChecker:
    @staticmethod
    def check_internet():
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=5)
            print("[OK] Internet")
            return True
        except OSError:
            print("[FAIL] Internet")
            return False

    @staticmethod
    def check_clearml_service(url):
        try:
            r = requests.get(url + "/auth.login", timeout=5)
            if r.status_code in [200, 401]:
                print("[OK] ClearML Service")
                return True
            print(f"[FAIL] ClearML Service {r.status_code}")
            return False
        except Exception:
            print("[FAIL] ClearML Service")
            return False

    @staticmethod
    def check_clearml_auth(url, access_key, secret_key):
        try:
            creds = f"{access_key}:{secret_key}"
            auth_header = b64encode(creds.encode("utf-8")).decode("utf-8")
            r = requests.post(url + "/auth.login",
                              headers={"Authorization": f"Basic {auth_header}"},
                              timeout=5)
            if r.status_code == 200:
                print("[OK] ClearML Auth")
                return True
            print(f"[FAIL] ClearML Auth {r.status_code}")
            return False
        except Exception:
            print("[FAIL] ClearML Auth")
            return False


# ------------------------------
# Projects API
# ------------------------------
class ProjectsAPI:
    def __init__(self, post): self._post = post
    def create(self, name, description=""): return self._post("/projects.create", {"name": name, "description": description})
    def get_all(self): return self._post("/projects.get_all")['projects']


# ------------------------------
# Models API
# ------------------------------
class ModelsAPI:
    def __init__(self, post): self._post = post
    def create(self, name, project_id): return self._post("/models.create", {"name": name, "project": project_id, "uri": "s3://dummy/uri"})
    def get_all(self, project_id): return self._post("/models.get_all", {"project": project_id})['models']
    def get_by_id(self, model_id): return self._post("/models.get_by_id", {"model": model_id})
    def update(self, model_id, uri): return self._post("/models.update", {"model": model_id, "uri": uri})
    def delete(self, model_id): return self._post("/models.delete", {"model": model_id})


# ------------------------------
# MLOps Manager
# ------------------------------
class MLOpsManager:
    def __init__(self):
        self.clearml_url = "http://213.233.184.112:30008"
        self.clearml_access_key = "X30GQ3KMOE37W93XOVX9HPI82MDS4P"
        self.clearml_secret_key = "N0PejMsjvKazBv5-vtHeMrObTZuPQHMfQzJTPWa_5uK5p2ZtP0IjR1hBmm0y79uJAFY"

        self.ceph_url = "http://s3.cloud-ai.ir"
        self.ceph_access_key = "OAF0MC26UA7DV9WS11X5"
        self.ceph_secret_key = "6SY2dTxhcIVEsjbfpjRUBhe3k7mMJIjZpccwvw3d"
        self.user_name = "mohammad"
        self.ceph_bucket = "mlops"
        # self.ceph_bucket = f"user_{self.user_name}"

        if not HealthChecker.check_internet(): sys.exit(1)
        ceph_mgr = CephS3Manager(self.ceph_url, self.ceph_access_key, self.ceph_secret_key, self.ceph_bucket)
        ceph_mgr.ensure_bucket_exists()
        if not ceph_mgr.check_connection(): sys.exit(1)
        if not ceph_mgr.check_auth(): sys.exit(1)
        if not HealthChecker.check_clearml_service(self.clearml_url): sys.exit(1)
        if not HealthChecker.check_clearml_auth(self.clearml_url, self.clearml_access_key, self.clearml_secret_key): sys.exit(1)

        self.ceph = ceph_mgr

        creds = f"{self.clearml_access_key}:{self.clearml_secret_key}"
        auth_header = b64encode(creds.encode("utf-8")).decode("utf-8")
        res = requests.post(f"{self.clearml_url}/auth.login",
                            headers={"Authorization": f"Basic {auth_header}"})
        print("[DEBUG] auth.login:", res.text)
        self.token = res.json()['data']['token']

        self.projects = ProjectsAPI(self._post)
        self.models = ModelsAPI(self._post)

        projects = self.projects.get_all()
        print("[DEBUG] All Projects:", projects)
        self.project_name = f"project_{self.user_name}"
        exists = [p for p in projects if p['name'] == self.project_name]
        self.project_id = exists[0]['id'] if exists else self.projects.create(self.project_name)['id']

    def _post(self, path, params=None):
        headers = {"Authorization": f"Bearer {self.token}"}
        res = requests.post(f"{self.clearml_url}{path}", headers=headers, json=params)
        print(f"[DEBUG] POST {path} -> {res.status_code} -> {res.text}")
        return res.json()['data']

    def add_model(self, source_type, **kwargs):
        model_name = kwargs.get("model_name")
        model = self.models.create(name=model_name, project_id=self.project_id)
        print("[DEBUG] Model Create Response:", model)
        model_id = model['id']
        dest_prefix = f"models/{model_id}/"

        if source_type == "local":
            self.ceph.upload(kwargs.get("source_path"), dest_prefix)
        elif source_type == "hf":
            local_path = snapshot_download(repo_id=kwargs.get("hf_source"))
            self.ceph.upload(local_path, dest_prefix)
        elif source_type == "s3":
            src_ceph = CephS3Manager(kwargs.get("endpoint_url"),
                                     kwargs.get("access_key"),
                                     kwargs.get("secret_key"),
                                     kwargs.get("bucket_name"))
            tmp = f"./tmp_{model_name}"
            src_ceph.download(kwargs.get("source_path"), tmp)
            self.ceph.upload(tmp, dest_prefix)
        else:
            raise ValueError("Unknown source_type")

        uri = f"s3://{self.ceph_bucket}/{dest_prefix}"
        self.models.update(model_id, uri)
        print(f"[AddModel] {model_id} {model_name}")
        return model_id

    def get_model(self, model_id, local_dest):
        model_data = self.models.get_by_id(model_id)
        if not model_data:
            print("[FAIL] Model not found")
            return
        model = model_data.get("model") or model_data
        uri = model['uri']
        _, remote_path = uri.replace("s3://", "").split("/", 1)
        self.ceph.download(remote_path, local_dest)
        print("[Info] Downloaded:", model)
        return model

    def list_models(self):
        models = self.models.get_all(self.project_id)
        for m in models:
            print(f"[Model] {m['id']} {m['name']}")
        return models

    def delete_model(self, model_id):
        model = self.models.get_by_id(model_id)
        uri = model['uri']
        _, remote_path = uri.replace("s3://", "").split("/", 1)
        self.ceph.delete_folder(remote_path)
        self.models.delete(model_id)
        print(f"[Deleted] {model_id}")


# ------------------------------
# Example
# ------------------------------
if __name__ == "__main__":
    manager = MLOpsManager()
    local_model_id = manager.add_model(
        source_type="local",
        source_path=r"C:\Users\ASUS\Desktop\Qwen2.5-14B-Instruct",
        model_name="local_model"
    )
    hf_model_id = manager.add_model(
        source_type="hf",
        hf_source="facebook/wav2vec2-base-960h",
        model_name="hf_model"
    )
    s3_model_id = manager.add_model(
        source_type="s3",
        endpoint_url="http://s3.cloud-ai.ir",
        access_key="OAF0MC26UA7DV9WS11X5",
        secret_key="6SY2dTxhcIVEsjbfpjRUBhe3k7mMJIjZpccwvw3d",
        bucket_name="mlops",
        source_path="models/llm-small/1.0/Qwen2.5-0.5B-Instruct/",
        model_name="s3_test_model"
    )
    manager.get_model(model_id=hf_model_id, local_dest="./downloads")
    manager.list_models()
    manager.delete_model(model_id=local_model_id)
