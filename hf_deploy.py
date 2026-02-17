import os
from huggingface_hub import HfApi, create_repo
from pathlib import Path

def deploy():
    repo_id = "MatverseHub/svca-lab-dataset"
    api = HfApi()
    
    print(f"🚀 Iniciando deploy para Hugging Face: {repo_id}")
    
    try:
        # Tenta criar o repo se não existir
        try:
            create_repo(repo_id=repo_id, repo_type="dataset", exist_ok=True)
            print(f"✅ Repositório {repo_id} verificado/criado.")
        except Exception as e:
            print(f"ℹ️ Nota ao criar repo: {e}")

        # Upload da pasta de artefatos
        api.upload_folder(
            folder_path="/home/ubuntu/svca-lab-genesis/artifact",
            repo_id=repo_id,
            repo_type="dataset",
            path_in_repo="artifact"
        )
        print("✅ Pasta artifact enviada.")

        # Upload da Evidence Note
        api.upload_file(
            path_or_fileobj="/home/ubuntu/svca-lab-genesis/EVIDENCE_NOTE.md",
            path_in_repo="EVIDENCE_NOTE.md",
            repo_id=repo_id,
            repo_type="dataset"
        )
        print("✅ EVIDENCE_NOTE.md enviada.")

        return True
    except Exception as e:
        print(f"❌ Erro no deploy HF: {e}")
        return False

if __name__ == "__main__":
    deploy()
