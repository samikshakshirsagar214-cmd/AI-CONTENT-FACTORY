from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle
from pathlib import Path

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# Get the project root directory (where client_secret.json should be)
PROJECT_ROOT = Path(__file__).parent.parent.parent
CLIENT_SECRET_PATH = PROJECT_ROOT / "client_secret.json"
TOKEN_PATH = PROJECT_ROOT / "token.pickle"


class UploadAgent:

    def __init__(self):
        self.youtube = None

    def authenticate(self):
        """
        Authenticate with YouTube API using OAuth2.
        
        REQUIRES: client_secret.json in project root
        See setup_youtube_credentials.py for instructions on obtaining credentials.
        """
        creds = None

        # [CACHE] Save login session (no login every time)
        if TOKEN_PATH.exists():
            try:
                with open(TOKEN_PATH, "rb") as token:
                    creds = pickle.load(token)
                print("[INFO] Loaded cached YouTube credentials")
            except Exception as e:
                print(f"[WARNING] Could not load cached credentials: {e}")

        # Check if credentials are valid and refresh if needed
        if creds and creds.expired and creds.refresh_token:
            try:
                print("[INFO] Refreshing expired YouTube credentials...")
                creds.refresh(Request())
                # Save refreshed credentials
                with open(TOKEN_PATH, "wb") as token:
                    pickle.dump(creds, token)
                print("[SUCCESS] YouTube credentials refreshed!")
            except Exception as e:
                print(f"[WARNING] Could not refresh credentials: {e}")
                print("[INFO] Deleting old token and will re-authenticate...")
                if TOKEN_PATH.exists():
                    TOKEN_PATH.unlink()  # Delete the expired token file
                creds = None

        if not creds or creds.expired:
            # Check if client_secret.json exists
            if not CLIENT_SECRET_PATH.exists():
                print("[ERROR] 'client_secret.json' not found!")
                print(f"[ERROR] Looking for: {CLIENT_SECRET_PATH}")
                print("[ERROR] YouTube authentication failed - upload will not work")
                print("[INFO] Run 'python setup_youtube_credentials.py' to set up authentication")
                return None
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(CLIENT_SECRET_PATH), SCOPES
                )

                print("[INFO] Opening browser for YouTube authentication...")
                creds = flow.run_local_server(port=0)

                # Save credentials for next time
                with open(TOKEN_PATH, "wb") as token:
                    pickle.dump(creds, token)
                print("[SUCCESS] YouTube authentication successful!")
                
            except PermissionError as e:
                print(f"[ERROR] Permission denied accessing client_secret.json: {e}")
                print("[ERROR] YouTube authentication skipped - upload will not work")
                return None
            except Exception as e:
                print(f"[ERROR] Authentication failed: {e}")
                print("[INFO] Run 'python setup_youtube_credentials.py' for help")
                return None

        return build("youtube", "v3", credentials=creds)
    
    def get_youtube(self):
        if self.youtube is None:
            self.youtube = self.authenticate()
        return self.youtube

    def upload(self, video_file, title, description=None):

        if description is None:
            description = ""
        
        print("[UPLOAD] Uploading to YouTube...")
        
        youtube = self.get_youtube()
        if youtube is None:
            print("[ERROR] Cannot upload - YouTube not authenticated")
            return None

        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title[:100],
                    "description": description + "\n\n#shorts",
                    "tags": ["AI", "Shorts", "Automation", "Trending"],
                    "categoryId": "28",
                },
                "status": {
                    "privacyStatus": "public"
                },
            },
            media_body=MediaFileUpload(video_file, resumable=True)
        )

        try:
            response = request.execute()
            print("[SUCCESS] Uploaded successfully!")
            print("[INFO] Video ID:", response["id"])
            return response
        except Exception as e:
            error_str = str(e).lower()
            if "invalid_grant" in error_str or "token" in error_str and ("expired" in error_str or "revoked" in error_str):
                print(f"[ERROR] Authentication error: {e}")
                print("[INFO] Token may be expired. Clearing cache and retrying...")
                
                # Clear the cached credentials and YouTube client
                if TOKEN_PATH.exists():
                    TOKEN_PATH.unlink()
                self.youtube = None
                
                # Retry authentication and upload
                youtube = self.get_youtube()
                if youtube is None:
                    print("[ERROR] Re-authentication failed")
                    return None
                
                # Rebuild the request with new credentials
                request = youtube.videos().insert(
                    part="snippet,status",
                    body={
                        "snippet": {
                            "title": title[:100],
                            "description": description + "\n\n#shorts",
                            "tags": ["AI", "Shorts", "Automation", "Trending"],
                            "categoryId": "28",
                        },
                        "status": {
                            "privacyStatus": "public"
                        },
                    },
                    media_body=MediaFileUpload(video_file, resumable=True)
                )
                
                try:
                    response = request.execute()
                    print("[SUCCESS] Uploaded successfully after re-authentication!")
                    print("[INFO] Video ID:", response["id"])
                    return response
                except Exception as retry_error:
                    print(f"[ERROR] Upload failed even after re-authentication: {retry_error}")
                    return None
            else:
                print(f"[ERROR] Upload failed: {e}")
                return None