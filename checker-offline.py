import time
import requests
import subprocess

M3U_FILE = 'lista.m3u'
LOG_FILE = 'offline.txt'
CHECK_INTERVAL = 1800  # 30 minutos

def carregar_links_m3u(arquivo):
    with open(arquivo, 'r', encoding='utf-8') as f:
        linhas = f.readlines()

    links = []
    nome_atual = None

    for linha in linhas:
        linha = linha.strip()
        if linha.startswith("#EXTINF:"):
            nome_atual = linha
        elif linha.startswith("http"):
            links.append((nome_atual, linha))
    return links

def verificar_link(nome, url):
    try:
        response = requests.get(url, timeout=10, stream=True)
        if response.status_code == 200:
            print(f"[ONLINE] {nome}")
            return True
        else:
            print(f"[OFFLINE] {nome}")
            return False
    except:
        print(f"[OFFLINE] {nome}")
        return False

def salvar_offlines(offline):
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        for nome, url in offline:
            f.write(f"{nome}\n{url}\n\n")

    try:
        subprocess.run(["git", "add", LOG_FILE], check=True)
        subprocess.run(["git", "commit", "-m", "Atualização automática dos canais offline"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("📤 offline.txt enviado para o GitHub.")
    except Exception as e:
        print(f"Erro ao enviar para o GitHub: {e}")

def rodar_checker():
    print("🔄 Iniciando verificação...")
    canais = carregar_links_m3u(M3U_FILE)
    offline = []

    for nome, url in canais:
        if not verificar_link(nome, url):
            offline.append((nome, url))

    salvar_offlines(offline)
    print(f"✅ Verificação completa. {len(offline)} canais offline.\n")

if __name__ == "__main__":
    while True:
        rodar_checker()
        print(f"⏳ Aguardando {CHECK_INTERVAL // 60} minutos...\n")
        time.sleep(CHECK_INTERVAL)
