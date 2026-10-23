from pathlib import Path

URL = " https://www.meteociel.fr/obs/foudre/latest2h.gif" 
# 15dernière minutes France "https://www.meteociel.fr/obs/foudre/latest.gif"
	
OUT_DIR = Path("data/images")
INTERVAL_S = 300        # 5 min minimum
MAX_BACKOFF_S = 3600 