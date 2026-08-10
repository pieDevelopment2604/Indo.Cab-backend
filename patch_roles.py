import glob

files = glob.glob("app/routes/*.py")
for f in files:
    with open(f, "r") as file:
        content = file.read()
    if "role_required" in content:
        content = content.replace("role_required", "RoleChecker")
        content = content.replace("[\"ADMIN\"]", "[UserRole.ADMIN]")
        content = content.replace("[\"ADMIN\", \"VENDOR\"]", "[UserRole.ADMIN, UserRole.VENDOR]")
        content = content.replace("[\"ADMIN\", \"VENDOR\", \"DRIVER\"]", "[UserRole.ADMIN, UserRole.VENDOR, UserRole.DRIVER]")
        content = content.replace("[\"ADMIN\", \"USER\", \"VENDOR\"]", "[UserRole.ADMIN, UserRole.USER, UserRole.VENDOR]")
        content = content.replace("[\"ADMIN\", \"USER\", \"VENDOR\", \"DRIVER\"]", "[UserRole.ADMIN, UserRole.USER, UserRole.VENDOR, UserRole.DRIVER]")
        if "UserRole" not in content:
            content = content.replace("from app.models.user import User", "from app.models.user import User, UserRole")
        with open(f, "w") as file:
            file.write(content)
