# import bcrypt
# import base64
# from datetime import datetime
# from firebase_config import init_firebase
# from engine import generate_access_code, generate_totp_secret

# fire_db = init_firebase()

# def hash_password(password):
#     return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# def verify_password(password, hashed):
#     return bcrypt.checkpw(password.encode(), hashed.encode())

# def submit_request(org_name, contact_name, contact_email, org_type, reason):
#     existing = fire_db.collection("access_requests").where(
#         "contact_email", "==", contact_email.strip()).stream()
#     if any(True for _ in existing):
#         return False, "A request with this email already exists."
#     fire_db.collection("access_requests").add({
#         "org_name": org_name,
#         "contact_name": contact_name,
#         "contact_email": contact_email.strip(),
#         "org_type": org_type,
#         "reason": reason,
#         "status": "pending",
#         "submitted_at": datetime.now().isoformat()
#     })
#     return True, "Request submitted successfully."

# def check_request_status(email):
#     email = email.strip()
#     # First, check if they are already in the approved organisations collection
#     orgs = fire_db.collection("organisations").where("contact_email", "==", email).stream()
#     for o in orgs:
#         d = o.to_dict()
#         return {
#             "status": "approved", 
#             "org_name": d.get("name", ""),
#             "access_code": d.get("access_code", ""),
#             "totp_secret": d.get("totp_secret", "")
#         }
    
#     # If not approved yet, check the pending requests
#     reqs = fire_db.collection("access_requests").where("contact_email", "==", email).stream()
#     for r in reqs:
#         d = r.to_dict()
#         if d.get("status") == "pending":
#             return {"status": "pending"}
#         elif d.get("status") == "rejected":
#             return {"status": "rejected"}
            
#     return {"status": "not_found"}
    
# def get_pending_requests():
#     reqs = fire_db.collection("access_requests").where("status", "==", "pending").stream()
#     return [{"id": r.id, **r.to_dict()} for r in reqs]

# def approve_request(req_id, req_data, password):
#     access_code = generate_access_code()
#     totp_secret = generate_totp_secret()
#     password_hash = hash_password(password)
#     fire_db.collection("organisations").add({
#         "name": req_data["org_name"],
#         "contact_name": req_data["contact_name"],
#         "contact_email": req_data["contact_email"],
#         "access_code": access_code,
#         "password_hash": password_hash,
#         "totp_secret": totp_secret,
#         "status": "active",
#         "approved_at": datetime.now().isoformat()
#     })
#     fire_db.collection("access_requests").document(req_id).update({"status": "approved"})
#     return access_code, totp_secret

# def reject_request(req_id):
#     fire_db.collection("access_requests").document(req_id).update({"status": "rejected"})

# def get_org_by_access_code(access_code):
#     orgs = fire_db.collection("organisations").where(
#         "access_code", "==", access_code.strip()).stream()
#     org_list = [{"id": o.id, **o.to_dict()} for o in orgs]
#     return org_list[0] if org_list else None

# def get_all_orgs():
#     orgs = fire_db.collection("organisations").stream()
#     return [{"id": o.id, **o.to_dict()} for o in orgs]

# def revoke_org(org_id):
#     fire_db.collection("organisations").document(org_id).delete()

# def toggle_org_status(org_id, current_status):
#     new_status = "suspended" if current_status == "active" else "active"
#     fire_db.collection("organisations").document(org_id).update({"status": new_status})

# def register_asset(org_id, org_name, asset_name, filename, hashes, img_bytes):
#     b64 = base64.b64encode(img_bytes).decode()
#     fire_db.collection("registered_assets").add({
#         "org_id": org_id,
#         "org_name": org_name,
#         "asset_name": asset_name,
#         "filename": filename,
#         "hashes": hashes,
#         "img_data": b64,
#         "registered_at": datetime.now().isoformat()
#     })

# def get_all_assets():
#     assets = fire_db.collection("registered_assets").stream()
#     return [a.to_dict() for a in assets]

# def get_org_assets(org_id):
#     assets = fire_db.collection("registered_assets").where("org_id", "==", org_id).stream()
#     return [a.to_dict() for a in assets]

# def get_org_asset_count(org_id):
#     assets = fire_db.collection("registered_assets").where("org_id", "==", org_id).stream()
#     return sum(1 for _ in assets)

import bcrypt, base64
from datetime import datetime
from firebase_config import init_firebase
from engine import generate_access_code, generate_totp_secret

fire_db = init_firebase()

# ─────────────────────────────────────────
# PASSWORD
# ─────────────────────────────────────────
def hash_password(p):
    return bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()

def verify_password(p, h):
    return bcrypt.checkpw(p.encode(), h.encode())

# ─────────────────────────────────────────
# ACCESS REQUESTS
# ─────────────────────────────────────────
def submit_request(org_name, contact_name, contact_email, org_type, reason):
    existing = fire_db.collection("access_requests").where(
        "contact_email", "==", contact_email.strip()).stream()
    if any(True for _ in existing):
        return False, "A request with this email already exists."
    fire_db.collection("access_requests").add({
        "org_name": org_name,
        "contact_name": contact_name,
        "contact_email": contact_email.strip(),
        "org_type": org_type,
        "reason": reason,
        "status": "pending",
        "submitted_at": datetime.now().isoformat()
    })
    return True, "Request submitted."

def check_request_status(email):
    email = email.strip()
    for o in fire_db.collection("organisations").where("contact_email", "==", email).stream():
        return {"status": "approved", "org_name": o.to_dict().get("name", "")}
    for r in fire_db.collection("access_requests").where("contact_email", "==", email).stream():
        s = r.to_dict().get("status")
        if s in ("pending", "rejected"):
            return {"status": s}
    return {"status": "not_found"}

def get_pending_requests():
    return [{"id": r.id, **r.to_dict()}
            for r in fire_db.collection("access_requests").where("status", "==", "pending").stream()]

# ─────────────────────────────────────────
# ORGANISATIONS
# ─────────────────────────────────────────
def approve_request(req_id, req_data, password):
    code = generate_access_code()
    secret = generate_totp_secret()
    fire_db.collection("organisations").add({
        "name": req_data["org_name"],
        "contact_name": req_data["contact_name"],
        "contact_email": req_data["contact_email"],
        "access_code": code,
        "password_hash": hash_password(password),
        "totp_secret": secret,
        "status": "active",
        "approved_at": datetime.now().isoformat()
    })
    fire_db.collection("access_requests").document(req_id).update({"status": "approved"})
    return code, secret

def reject_request(req_id):
    fire_db.collection("access_requests").document(req_id).update({"status": "rejected"})

def get_org_by_access_code(code):
    orgs = [{"id": o.id, **o.to_dict()}
            for o in fire_db.collection("organisations").where(
                "access_code", "==", code.strip()).stream()]
    return orgs[0] if orgs else None

def get_all_orgs():
    return [{"id": o.id, **o.to_dict()}
            for o in fire_db.collection("organisations").stream()]

def revoke_org(org_id):
    fire_db.collection("organisations").document(org_id).delete()

def toggle_org_status(org_id, current):
    fire_db.collection("organisations").document(org_id).update({
        "status": "suspended" if current == "active" else "active"
    })

# ─────────────────────────────────────────
# ORG ADMIN MANAGEMENT (Point 3)
# ─────────────────────────────────────────
def update_org_contact(org_id, new_contact_name, new_contact_email):
    """Super admin can update contact person if original admin leaves"""
    fire_db.collection("organisations").document(org_id).update({
        "contact_name": new_contact_name,
        "contact_email": new_contact_email,
        "contact_updated_at": datetime.now().isoformat()
    })

def reset_org_password(org_id, new_password):
    """Super admin can reset org password"""
    fire_db.collection("organisations").document(org_id).update({
        "password_hash": hash_password(new_password),
        "password_reset_at": datetime.now().isoformat()
    })

def regenerate_org_access_code(org_id):
    """Super admin can generate new access code"""
    new_code = generate_access_code()
    fire_db.collection("organisations").document(org_id).update({
        "access_code": new_code,
        "code_regenerated_at": datetime.now().isoformat()
    })
    return new_code

def regenerate_org_2fa(org_id):
    """Super admin can reset 2FA if org admin loses their phone"""
    new_secret = generate_totp_secret()
    fire_db.collection("organisations").document(org_id).update({
        "totp_secret": new_secret,
        "2fa_reset_at": datetime.now().isoformat()
    })
    return new_secret

# ─────────────────────────────────────────
# ASSETS
# ─────────────────────────────────────────
def register_asset(org_id, org_name, asset_name, filename, hashes, img_bytes):
    fire_db.collection("registered_assets").add({
        "org_id": org_id,
        "org_name": org_name,
        "asset_name": asset_name,
        "filename": filename,
        "hashes": hashes,
        "img_data": base64.b64encode(img_bytes).decode(),
        "registered_at": datetime.now().isoformat()
    })

def get_all_assets():
    return [a.to_dict() for a in fire_db.collection("registered_assets").stream()]

def get_org_assets(org_id):
    return [a.to_dict() for a in fire_db.collection("registered_assets").where(
        "org_id", "==", org_id).stream()]

def get_org_asset_count(org_id):
    return sum(1 for _ in fire_db.collection("registered_assets").where(
        "org_id", "==", org_id).stream())