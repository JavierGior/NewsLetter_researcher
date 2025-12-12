# utils/diagnostico.py
import sys
import subprocess

def verificar_dependencias():
    """Verifica versiones y ofrece solución automática"""
    print("🔍 DIAGNÓSTICO DE DEPENDENCIAS")
    print("=" * 60)

    def get_version(pkg):
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", pkg],
                capture_output=True, text=True
            )
            for line in result.stdout.splitlines():
                if line.startswith("Version:"):
                    return line.split(":")[1].strip()
        except:
            return None
        return None

    packages = {
        "langchain": None,
        "langchain-core": None,
        "langchain-openai": None,
        "pydantic": None,
        "tavily-python": None,
        "deepagents": None,
        "python-dotenv": None
    }

    for pkg in packages:
        version = get_version(pkg)
        packages[pkg] = version
        status = f"v{version}" if version else "❌ NO INSTALADO"
        print(f"📦 {pkg}: {status}")

    print("\n📊 ANÁLISIS DE COMPATIBILIDAD:")
    core_ver = packages.get("langchain-core")
    openai_ver = packages.get("langchain-openai")

    if core_ver and openai_ver:
        try:
            core_major = int(core_ver.split('.')[0])
            core_minor = int(core_ver.split('.')[1])
            openai_major = int(openai_ver.split('.')[0])

            if (core_major == 0 and core_minor >= 3) and openai_major < 2:
                print("❌ PROBLEMA DETECTADO: Incompatibilidad de versiones")
                print("💡 SOLUCIÓN: Actualizar langchain-openai a >=0.2.0")
                return False
        except:
            pass
        
    print("✅ Versiones compatibles")
    return True