"""版本管理"""

VERSION = "1.0.0"
RELEASE_DATE = "2025-01-06"
CODENAME = "Genesis"

def get_version_info():
    """获取版本信息"""
    return {
        "version": VERSION,
        "release_date": RELEASE_DATE,
        "codename": CODENAME,
        "python_requires": ">=3.8",
    }
