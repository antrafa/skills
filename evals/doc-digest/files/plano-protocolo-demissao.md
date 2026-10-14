# Protocolo de Demissão (Ubuntu Linux) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Desenvolver um script bash autocontido, seguro e modular (`protocolo-demissao.sh`) para higienização e limpeza de estações de trabalho corporativas com Ubuntu Linux, cobrindo navegadores, credenciais de dev, nuvem, mensageiros, diretórios pessoais e caminhos customizados.

**Architecture:** Script executável único em Bash puro com design funcional e modular. Cada módulo de limpeza é encapsulado em funções dedicadas com flags de ativação declarativas (`CLEAN_*`). Conta com barreira anti-root, sanitização de caminhos via `safe_remove`, modo `--dry-run` para pré-visualização não-destrutiva e confirmação explícita obrigatória via digitação de `CONFIRMAR`.

**Tech Stack:** Bash 4+, Linux Coreutils (`rm`, `du`, `find`, `killall`/`pkill`), Bats ou scripts de teste em sandbox bash isolado (`TMPDIR`).

**Spec:** [docs/superpowers/specs/2026-09-18-protocolo-demissao-design.md](docs/superpowers/specs/2026-09-18-protocolo-demissao-design.md)

## Global Constraints

- Plataforma alvo: Ubuntu Linux exclusivamente.
- Sem dependências externas além do sistema base do Ubuntu (Bash e utilitários GNU coreutils).
- Bloqueio estrito se executado como `root`/`sudo`.
- Sanitização de caminhos: nunca permitir remoção de `/`, `/home`, `/root`, `/etc`, `/usr` ou caminhos vazios.
- Preservação da integridade do sistema: pastas pessoais padrão (`~/Downloads`, etc.) devem ter seus conteúdos esvaziados sem deletar a pasta-raiz XDG para não quebrar a interface gráfica.
- Cobertura de empacotamento nativo (`apt`), Snap e Flatpak nos alvos suportados.

---

### Task 1: Estrutura Base, Configuração, Travas de Segurança e Motor de Dry-Run

**Files:**
- Create: `protocolo-demissao.sh`
- Create: `tests/test_safety.sh`

**Interfaces:**
- Produces:
  - `check_not_root()`: encerra com código 1 se `EUID == 0`.
  - `parse_args("$@")`: processa `--dry-run`, `--force`, `--help`.
  - `safe_remove(target_path, is_dir_content_only)`: valida o caminho contra lista negra e executa `rm -rf` ou apenas exibe em modo dry-run.
  - `confirm_execution()`: exige a digitação de `CONFIRMAR` a menos que `--force` ou `--dry-run` estejam ativos.

- [ ] **Step 1: Escrever teste de segurança e parsing de argumentos**

```bash
mkdir -p tests
cat << 'EOF' > tests/test_safety.sh
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_SCRIPT="${SCRIPT_DIR}/protocolo-demissao.sh"

echo "=== Testando --help ==="
output=$("${TARGET_SCRIPT}" --help)
if [[ "${output}" != *"Uso: "* ]]; then
    echo "FALHA: --help não retornou instrução de uso."
    exit 1
fi

echo "=== Testando safe_remove com caminho proibido (/) ==="
export TEST_RUN=1
source "${TARGET_SCRIPT}" --source-only 2>/dev/null || true

# Testar se safe_remove bloqueia caminhos críticos
if safe_remove "/" 0 2>/dev/null; then
    echo "FALHA: safe_remove não bloqueou /"
    exit 1
fi

if safe_remove "" 0 2>/dev/null; then
    echo "FALHA: safe_remove não bloqueou caminho vazio"
    exit 1
fi

echo "=== Testes de Segurança passaram com sucesso! ==="
EOF
chmod +x tests/test_safety.sh
```

- [ ] **Step 2: Executar teste e verificar que falha (script ainda não existe)**

Run: `tests/test_safety.sh`
Expected: FAIL com arquivo `protocolo-demissao.sh` não encontrado ou comando falhando.

- [ ] **Step 3: Implementar a estrutura base, travas de segurança e safe_remove**

Criar `protocolo-demissao.sh`:
```bash
#!/usr/bin/env bash
# ==============================================================================
# PROTOCOLO DE DEMISSÃO - Higienização de Estações Ubuntu Linux
# ==============================================================================
set -eo pipefail

# --- CONFIGURAÇÃO DE ATIVAÇÃO DOS MÓDULOS ---
CLEAN_BROWSERS=true          # Google Chrome, Chromium, Firefox, Brave, Edge
CLEAN_DEV_CREDENTIALS=true   # SSH, GPG, Git configs e tokens
CLEAN_CLOUD_INFRA=true       # AWS, GCP, Azure, Kubernetes, Docker
CLEAN_DEV_TOKENS=true        # npm, pip, cargo, composer, gradle, maven, .netrc
CLEAN_IDES=true              # VS Code, JetBrains, Cursor
CLEAN_COMMUNICATION=true     # Slack, Discord, Microsoft Teams, Telegram
CLEAN_USER_DIRS=true         # Downloads, Documentos, Desktop, Imagens, Vídeos, Música
CLEAN_SHELL_HISTORY=true     # .bash_history, .zsh_history e histórico de terminal
CLEAN_TRASH=true             # Lixeira do Ubuntu (~/.local/share/Trash)

# --- PASTAS CUSTOMIZADAS ---
CUSTOM_PATHS=(
    # "$HOME/projetos"
    # "$HOME/workspace"
)

# --- CORES E FORMATAÇÃO ---
COLOR_RESET="\033[0m"
COLOR_RED="\033[1;31m"
COLOR_GREEN="\033[1;32m"
COLOR_YELLOW="\033[1;33m"
COLOR_BLUE="\033[1;34m"
COLOR_CYAN="\033[1;36m"
COLOR_GRAY="\033[0;90m"

log_info()    { echo -e "${COLOR_BLUE}[INFO]${COLOR_RESET} $*"; }
log_success() { echo -e "${COLOR_GREEN}[OK]${COLOR_RESET} $*"; }
log_warn()    { echo -e "${COLOR_YELLOW}[AVISO]${COLOR_RESET} $*"; }
log_error()   { echo -e "${COLOR_RED}[ERRO]${COLOR_RESET} $*"; }
log_dry()     { echo -e "${COLOR_YELLOW}[DRY-RUN]${COLOR_RESET} $*"; }
log_skip()    { echo -e "${COLOR_GRAY}[IGNORADO]${COLOR_RESET} $*"; }

DRY_RUN=false
FORCE=false

check_not_root() {
    if [[ "${EUID}" -eq 0 ]]; then
        log_error "Este script NÃO deve ser executado com sudo ou como root!"
        log_error "Execute como o usuário comum dono dos arquivos que serão limpos."
        exit 1
    fi
}

safe_remove() {
    local target="$1"
    local content_only="${2:-0}"

    if [[ -z "${target}" ]]; then
        return 1
    fi

    # Normalizar caminho
    local clean_target
    clean_target="$(echo "${target}" | sed 's:/*$::')"
    [[ -z "${clean_target}" ]] && clean_target="/"

    # Lista negra de segurança absoluta
    case "${clean_target}" in
        "/"|"/home"|"/root"|"/bin"|"/boot"|"/dev"|"/etc"|"/lib"|"/lib64"|"/usr"|"/var"|"/proc"|"/sys"|"/tmp")
            log_error "Tentativa de remoção de caminho crítico bloqueada: ${target}"
            return 1
            ;;
    esac

    if [[ "${content_only}" -eq 1 ]]; then
        if [[ ! -d "${target}" ]]; then
            log_skip "Diretório não existe: ${target}"
            return 0
        fi

        local count
        count=$(find "${target}" -mindepth 1 -maxdepth 1 2>/dev/null | wc -l)
        if [[ "${count}" -eq 0 ]]; then
            log_skip "Diretório já está vazio: ${target}"
            return 0
        fi

        if [[ "${DRY_RUN}" == true ]]; then
            log_dry "Esvaziaria o conteúdo de: ${target} (${count} itens)"
        else
            find "${target}" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} + 2>/dev/null || true
            log_success "Conteúdo esvaziado: ${target}"
        fi
        return 0
    fi

    if [[ ! -e "${target}" ]]; then
        log_skip "Não encontrado: ${target}"
        return 0
    fi

    local size="-"
    size=$(du -sh "${target}" 2>/dev/null | cut -f1 || echo "-")

    if [[ "${DRY_RUN}" == true ]]; then
        log_dry "Removeria: ${target} (${size})"
    else
        rm -rf -- "${target}" 2>/dev/null || true
        log_success "Removido: ${target} (${size})"
    fi
}

show_help() {
    cat << EOF
Uso: $(basename "$0") [OPÇÕES]

Script seguro para higienização e protocolo de desligamento no Ubuntu Linux.

Opções:
  --dry-run       Simula a execução e lista tudo o que seria removido sem alterar nada.
  --force         Pula a confirmação manual via digitação de 'CONFIRMAR'.
  -h, --help      Exibe esta ajuda.

Edite o topo do arquivo $(basename "$0") para habilitar/desabilitar módulos ou adicionar pastas em CUSTOM_PATHS.
EOF
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --force)
                FORCE=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            --source-only)
                return 0
                ;;
            *)
                log_error "Opção desconhecida: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

confirm_execution() {
    if [[ "${DRY_RUN}" == true ]]; then
        log_info "Modo de simulação ativo (--dry-run). NENHUM arquivo será modificado."
        return 0
    fi

    if [[ "${FORCE}" == true ]]; then
        log_warn "Flag --force informada. Prosseguindo sem prompt de confirmação."
        return 0
    fi

    echo
    echo -e "${COLOR_RED}============================== ATENÇÃO ==============================${COLOR_RESET}"
    echo -e "${COLOR_YELLOW}Este script apagará dados de histórico, credenciais e pastas configuradas!${COLOR_RESET}"
    echo -e "${COLOR_RED}Essa ação é irreversível.${COLOR_RESET}"
    echo -e "${COLOR_RED}=====================================================================${COLOR_RESET}"
    echo
    read -rp "Para confirmar a execução, digite exatamente 'CONFIRMAR': " response
    if [[ "${response}" != "CONFIRMAR" ]]; then
        log_info "Execução cancelada pelo usuário."
        exit 0
    fi
}

# Se chamado diretamente (não como source em teste)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    check_not_root
    parse_args "$@"
    confirm_execution
fi
```
Tornar executável com `chmod +x protocolo-demissao.sh`.

- [ ] **Step 4: Executar testes de segurança e verificar aprovação**

Run: `tests/test_safety.sh`
Expected: PASS com "Testes de Segurança passaram com sucesso!"

- [ ] **Step 5: Commit**

```bash
git add protocolo-demissao.sh tests/test_safety.sh
git commit -m "feat: add base script, safety guards, and dry-run engine"
```

---

### Task 2: Módulo de Encerramento de Processos e Limpeza de Navegadores

**Files:**
- Modify: `protocolo-demissao.sh`
- Create: `tests/test_browsers.sh`

**Interfaces:**
- Produces:
  - `kill_running_processes()`: encerra instâncias de navegadores e mensageiros silenciosamente.
  - `clean_browsers()`: varre e limpa Chrome, Chromium, Firefox, Brave e Edge (nativo, snap e flatpak).

- [ ] **Step 1: Escrever teste para o módulo de navegadores em sandbox temporária**

```bash
cat << 'EOF' > tests/test_browsers.sh
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_SCRIPT="${SCRIPT_DIR}/protocolo-demissao.sh"

# Cria ambiente isolado fingindo ser o HOME
FAKE_HOME=$(mktemp -d /tmp/fake_home_test.XXXXXX)
trap 'rm -rf "${FAKE_HOME}"' EXIT

mkdir -p "${FAKE_HOME}/.config/google-chrome/Default"
mkdir -p "${FAKE_HOME}/.mozilla/firefox/profile.default"
mkdir -p "${FAKE_HOME}/snap/firefox/common"
echo "historico" > "${FAKE_HOME}/.config/google-chrome/Default/History"
echo "cookies" > "${FAKE_HOME}/.mozilla/firefox/profile.default/cookies.sqlite"

# Carregar script com HOME apontando para o FAKE_HOME
export HOME="${FAKE_HOME}"
source "${TARGET_SCRIPT}" --source-only

echo "=== Testando clean_browsers no sandbox ==="
DRY_RUN=false
clean_browsers

if [[ -d "${FAKE_HOME}/.config/google-chrome" ]]; then
    echo "FALHA: Diretório google-chrome ainda existe!"
    exit 1
fi

if [[ -d "${FAKE_HOME}/.mozilla" ]]; then
    echo "FALHA: Diretório .mozilla ainda existe!"
    exit 1
fi

if [[ -d "${FAKE_HOME}/snap/firefox" ]]; then
    echo "FALHA: Diretório snap/firefox ainda existe!"
    exit 1
fi

echo "=== Teste de Navegadores passou com sucesso! ==="
EOF
chmod +x tests/test_browsers.sh
```

- [ ] **Step 2: Executar teste e verificar que falha (clean_browsers não implementado)**

Run: `tests/test_browsers.sh`
Expected: FAIL com `clean_browsers: command not found`.

- [ ] **Step 3: Implementar `kill_running_processes` e `clean_browsers` em `protocolo-demissao.sh`**

Adicionar funções a `protocolo-demissao.sh`:
```bash
kill_running_processes() {
    log_info "Encerrando processos de navegadores e aplicativos..."
    local apps=(
        "chrome" "google-chrome" "chromium" "chromium-browser"
        "firefox" "brave" "msedge" "edge"
        "slack" "discord" "teams" "telegram-desktop"
    )
    for app in "${apps[@]}"; do
        if pkill -f "${app}" 2>/dev/null; then
            log_info "Processo encerrado: ${app}"
        fi
    done
    sleep 1
}

clean_browsers() {
    [[ "${CLEAN_BROWSERS}" != true ]] && return 0
    log_info "Limpando navegadores (histórico, perfis, cache e cookies)..."

    local browser_targets=(
        # Google Chrome / Chromium
        "${HOME}/.config/google-chrome"
        "${HOME}/.cache/google-chrome"
        "${HOME}/.config/chromium"
        "${HOME}/.cache/chromium"
        "${HOME}/snap/chromium"
        "${HOME}/snap/google-chrome"
        "${HOME}/.var/app/com.google.Chrome"
        "${HOME}/.var/app/org.chromium.Chromium"

        # Mozilla Firefox
        "${HOME}/.mozilla"
        "${HOME}/.cache/mozilla"
        "${HOME}/snap/firefox"
        "${HOME}/.var/app/org.mozilla.firefox"

        # Brave
        "${HOME}/.config/BraveSoftware"
        "${HOME}/.cache/BraveSoftware"
        "${HOME}/snap/brave"
        "${HOME}/.var/app/com.brave.Browser"

        # Microsoft Edge
        "${HOME}/.config/microsoft-edge"
        "${HOME}/.cache/microsoft-edge"
        "${HOME}/.var/app/com.microsoft.Edge"

        # Opera / Vivaldi
        "${HOME}/.config/opera"
        "${HOME}/.config/vivaldi"
    )

    for target in "${browser_targets[@]}"; do
        safe_remove "${target}"
    done
}
```

- [ ] **Step 4: Executar teste e verificar aprovação**

Run: `tests/test_browsers.sh`
Expected: PASS com "Teste de Navegadores passou com sucesso!"

- [ ] **Step 5: Commit**

```bash
git add protocolo-demissao.sh tests/test_browsers.sh
git commit -m "feat: add process termination and browser cleanup module"
```

---

### Task 3: Módulos de Credenciais de Desenvolvimento, Nuvem/DevOps e Tokens de Pacotes

**Files:**
- Modify: `protocolo-demissao.sh`
- Create: `tests/test_credentials.sh`

**Interfaces:**
- Produces:
  - `clean_dev_credentials()`: remove chaves SSH, GPG e credenciais Git.
  - `clean_cloud_infra()`: remove configs de AWS, GCP, Azure, Kubernetes, Docker, Terraform e Helm.
  - `clean_dev_tokens()`: remove tokens de npm, yarn, pnpm, pip, cargo, composer, JVM e .netrc.

- [ ] **Step 1: Escrever teste de credenciais e tokens em sandbox**

```bash
cat << 'EOF' > tests/test_credentials.sh
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_SCRIPT="${SCRIPT_DIR}/protocolo-demissao.sh"

FAKE_HOME=$(mktemp -d /tmp/fake_cred_test.XXXXXX)
trap 'rm -rf "${FAKE_HOME}"' EXIT

mkdir -p "${FAKE_HOME}/.ssh"
mkdir -p "${FAKE_HOME}/.aws"
mkdir -p "${FAKE_HOME}/.kube"
mkdir -p "${FAKE_HOME}/.docker"
touch "${FAKE_HOME}/.ssh/id_rsa"
touch "${FAKE_HOME}/.gitconfig"
touch "${FAKE_HOME}/.git-credentials"
touch "${FAKE_HOME}/.npmrc"
touch "${FAKE_HOME}/.pypirc"

export HOME="${FAKE_HOME}"
source "${TARGET_SCRIPT}" --source-only

echo "=== Testando clean_dev_credentials, clean_cloud_infra e clean_dev_tokens ==="
DRY_RUN=false
clean_dev_credentials
clean_cloud_infra
clean_dev_tokens

for path in ".ssh" ".aws" ".kube" ".docker" ".gitconfig" ".git-credentials" ".npmrc" ".pypirc"; do
    if [[ -e "${FAKE_HOME}/${path}" ]]; then
        echo "FALHA: ${path} ainda existe!"
        exit 1
    fi
done

echo "=== Teste de Credenciais passou com sucesso! ==="
EOF
chmod +x tests/test_credentials.sh
```

- [ ] **Step 2: Executar teste e verificar que falha**

Run: `tests/test_credentials.sh`
Expected: FAIL com funções não encontradas.

- [ ] **Step 3: Implementar `clean_dev_credentials`, `clean_cloud_infra` e `clean_dev_tokens`**

Adicionar a `protocolo-demissao.sh`:
```bash
clean_dev_credentials() {
    [[ "${CLEAN_DEV_CREDENTIALS}" != true ]] && return 0
    log_info "Limpando credenciais de desenvolvimento (SSH, GPG, Git)..."

    # Encerrar cache de credenciais do git em memória
    git credential-cache exit 2>/dev/null || true

    local cred_targets=(
        "${HOME}/.ssh"
        "${HOME}/.gnupg"
        "${HOME}/.gitconfig"
        "${HOME}/.git-credentials"
        "${HOME}/.config/git"
    )

    for target in "${cred_targets[@]}"; do
        safe_remove "${target}"
    done
}

clean_cloud_infra() {
    [[ "${CLEAN_CLOUD_INFRA}" != true ]] && return 0
    log_info "Limpando configurações de nuvem e DevOps (AWS, GCP, Azure, Kube, Docker)..."

    local cloud_targets=(
        "${HOME}/.aws"
        "${HOME}/.config/gcloud"
        "${HOME}/.azure"
        "${HOME}/.kube"
        "${HOME}/.minikube"
        "${HOME}/.k9s"
        "${HOME}/.docker"
        "${HOME}/.terraform.d"
        "${HOME}/.terraformrc"
        "${HOME}/.config/helm"
        "${HOME}/.cache/helm"
        "${HOME}/.vault-token"
    )

    for target in "${cloud_targets[@]}"; do
        safe_remove "${target}"
    done
}

clean_dev_tokens() {
    [[ "${CLEAN_DEV_TOKENS}" != true ]] && return 0
    log_info "Limpando tokens de gerenciadores de pacotes..."

    local token_targets=(
        "${HOME}/.npmrc"
        "${HOME}/.yarnrc"
        "${HOME}/.yarnrc.yml"
        "${HOME}/.config/pnpm"
        "${HOME}/.pip/pip.conf"
        "${HOME}/.pypirc"
        "${HOME}/.cargo/credentials"
        "${HOME}/.cargo/credentials.toml"
        "${HOME}/.composer/auth.json"
        "${HOME}/.config/composer/auth.json"
        "${HOME}/.m2/settings.xml"
        "${HOME}/.m2/settings-security.xml"
        "${HOME}/.gradle/gradle.properties"
        "${HOME}/.netrc"
    )

    for target in "${token_targets[@]}"; do
        safe_remove "${target}"
    done
}
```

- [ ] **Step 4: Executar teste e verificar aprovação**

Run: `tests/test_credentials.sh`
Expected: PASS com "Teste de Credenciais passou com sucesso!"

- [ ] **Step 5: Commit**

```bash
git add protocolo-demissao.sh tests/test_credentials.sh
git commit -m "feat: add dev credentials, cloud infra and package tokens cleanup modules"
```

---

### Task 4: Módulos de IDEs, Mensageiros, Pastas de Usuário, Pastas Customizadas, Lixeira e Histórico

**Files:**
- Modify: `protocolo-demissao.sh`
- Create: `tests/test_user_and_custom.sh`

**Interfaces:**
- Produces:
  - `clean_ides()`: limpa dados recentes e workspaces do VS Code, Cursor e JetBrains.
  - `clean_communication()`: limpa sessões de Slack, Discord, Teams e Telegram.
  - `clean_user_dirs()`: esvazia o conteúdo de Downloads, Documentos, Desktop, etc. preservando a pasta pai.
  - `clean_custom_paths()`: remove com segurança os caminhos listados em `CUSTOM_PATHS`.
  - `clean_trash()`: esvazia a lixeira do Ubuntu.
  - `clean_shell_history()`: apaga arquivos de histórico e descarrega a memória da sessão.
  - `run_protocol()`: orquestrador que chama todos os módulos e exibe o resumo final.

- [ ] **Step 1: Escrever teste de pastas de usuário, custom paths e histórico em sandbox**

```bash
cat << 'EOF' > tests/test_user_and_custom.sh
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_SCRIPT="${SCRIPT_DIR}/protocolo-demissao.sh"

FAKE_HOME=$(mktemp -d /tmp/fake_user_test.XXXXXX)
CUSTOM_TEST_DIR=$(mktemp -d /tmp/fake_custom_dir.XXXXXX)
trap 'rm -rf "${FAKE_HOME}" "${CUSTOM_TEST_DIR}"' EXIT

mkdir -p "${FAKE_HOME}/Downloads"
touch "${FAKE_HOME}/Downloads/meu_boleto.pdf"
touch "${FAKE_HOME}/Downloads/foto.png"

mkdir -p "${FAKE_HOME}/.local/share/Trash/files"
touch "${FAKE_HOME}/.local/share/Trash/files/arquivo_deletado.txt"

touch "${FAKE_HOME}/.bash_history"
touch "${FAKE_HOME}/.zsh_history"

touch "${CUSTOM_TEST_DIR}/codigo_secreto.py"

export HOME="${FAKE_HOME}"
source "${TARGET_SCRIPT}" --source-only

CUSTOM_PATHS=("${CUSTOM_TEST_DIR}")
DRY_RUN=false

echo "=== Testando pastas pessoais, custom paths, trash e historico ==="
clean_user_dirs
clean_custom_paths
clean_trash
clean_shell_history

# Verifica se a pasta Downloads existe, mas seu conteúdo foi apagado
if [[ ! -d "${FAKE_HOME}/Downloads" ]]; then
    echo "FALHA: A pasta Downloads em si foi apagada!"
    exit 1
fi
if [[ -f "${FAKE_HOME}/Downloads/meu_boleto.pdf" ]]; then
    echo "FALHA: O arquivo dentro de Downloads não foi apagado!"
    exit 1
fi

# Verifica se custom path foi apagado
if [[ -e "${CUSTOM_TEST_DIR}" ]]; then
    echo "FALHA: CUSTOM_PATH ainda existe!"
    exit 1
fi

# Verifica se bash_history foi apagado
if [[ -f "${FAKE_HOME}/.bash_history" ]]; then
    echo "FALHA: .bash_history ainda existe!"
    exit 1
fi

echo "=== Teste de Pastas de Usuário e Custom Paths passou com sucesso! ==="
EOF
chmod +x tests/test_user_and_custom.sh
```

- [ ] **Step 2: Executar teste e verificar que falha**

Run: `tests/test_user_and_custom.sh`
Expected: FAIL com funções não encontradas.

- [ ] **Step 3: Implementar `clean_ides`, `clean_communication`, `clean_user_dirs`, `clean_custom_paths`, `clean_trash`, `clean_shell_history` e o `run_protocol` orquestrador**

Adicionar as funções restantes e integrar o fluxo principal em `protocolo-demissao.sh`:
```bash
clean_ides() {
    [[ "${CLEAN_IDES}" != true ]] && return 0
    log_info "Limpando workspaces e histórico de IDEs (VS Code, JetBrains, Cursor)..."

    local ide_targets=(
        "${HOME}/.config/Code/User/workspaceStorage"
        "${HOME}/.config/Code/User/history"
        "${HOME}/.config/Code/Backups"
        "${HOME}/.vscode"
        "${HOME}/snap/code"
        "${HOME}/.config/Cursor"
        "${HOME}/.cursor"
        "${HOME}/.config/VSCodium"
        "${HOME}/.config/JetBrains"
        "${HOME}/.local/share/JetBrains"
        "${HOME}/.cache/JetBrains"
    )

    for target in "${ide_targets[@]}"; do
        safe_remove "${target}"
    done
}

clean_communication() {
    [[ "${CLEAN_COMMUNICATION}" != true ]] && return 0
    log_info "Limpando dados e sessões de aplicativos de comunicação..."

    local comm_targets=(
        "${HOME}/.config/Slack"
        "${HOME}/.cache/Slack"
        "${HOME}/snap/slack"
        "${HOME}/.var/app/com.slack.Slack"
        "${HOME}/.config/discord"
        "${HOME}/snap/discord"
        "${HOME}/.var/app/com.discordapp.Discord"
        "${HOME}/.config/teams"
        "${HOME}/.config/Microsoft/Microsoft Teams"
        "${HOME}/.var/app/com.microsoft.Teams"
        "${HOME}/.local/share/TelegramDesktop"
        "${HOME}/snap/telegram-desktop"
        "${HOME}/.var/app/org.telegram.desktop"
    )

    for target in "${comm_targets[@]}"; do
        safe_remove "${target}"
    done
}

clean_user_dirs() {
    [[ "${CLEAN_USER_DIRS}" != true ]] && return 0
    log_info "Esvaziando conteúdo das pastas pessoais..."

    local user_dirs=(
        "${HOME}/Downloads"
        "${HOME}/Documents"
        "${HOME}/Documentos"
        "${HOME}/Desktop"
        "${HOME}/Área de Trabalho"
        "${HOME}/Pictures"
        "${HOME}/Imagens"
        "${HOME}/Videos"
        "${HOME}/Vídeos"
        "${HOME}/Music"
        "${HOME}/Música"
    )

    for dir in "${user_dirs[@]}"; do
        if [[ -d "${dir}" ]]; then
            safe_remove "${dir}" 1
        fi
    done
}

clean_custom_paths() {
    if [[ ${#CUSTOM_PATHS[@]} -eq 0 ]]; then
        return 0
    fi

    log_info "Processando pastas customizadas configuradas em CUSTOM_PATHS..."
    for custom in "${CUSTOM_PATHS[@]}"; do
        # Expandir til (~) se presente
        local expanded="${custom/#\~/$HOME}"
        safe_remove "${expanded}"
    done
}

clean_trash() {
    [[ "${CLEAN_TRASH}" != true ]] && return 0
    log_info "Esvaziando Lixeira..."

    local trash_dir="${HOME}/.local/share/Trash"
    if [[ -d "${trash_dir}" ]]; then
        safe_remove "${trash_dir}" 1
    fi
}

clean_shell_history() {
    [[ "${CLEAN_SHELL_HISTORY}" != true ]] && return 0
    log_info "Removendo históricos de comandos do shell..."

    local history_files=(
        "${HOME}/.bash_history"
        "${HOME}/.zsh_history"
        "${HOME}/.lesshst"
        "${HOME}/.python_history"
        "${HOME}/.node_repl_history"
        "${HOME}/.mysql_history"
        "${HOME}/.psql_history"
        "${HOME}/.sqlite_history"
        "${HOME}/.viminfo"
        "${HOME}/.local/share/nvim"
    )

    for hist in "${history_files[@]}"; do
        safe_remove "${hist}"
    done

    # Limpar buffer da sessão ativa se não for dry-run
    if [[ "${DRY_RUN}" != true ]]; then
        history -c 2>/dev/null || true
        history -w 2>/dev/null || true
    fi
}

run_protocol() {
    echo -e "${COLOR_CYAN}=====================================================${COLOR_RESET}"
    echo -e "${COLOR_CYAN}       INICIANDO PROTOCOLO DE DEMISSÃO               ${COLOR_RESET}"
    echo -e "${COLOR_CYAN}=====================================================${COLOR_RESET}"
    echo "Usuário alvo: ${USER} (${HOME})"
    echo "Modo Dry-Run: ${DRY_RUN}"
    echo

    if [[ "${DRY_RUN}" != true ]]; then
        kill_running_processes
    fi

    clean_browsers
    clean_dev_credentials
    clean_cloud_infra
    clean_dev_tokens
    clean_ides
    clean_communication
    clean_user_dirs
    clean_custom_paths
    clean_trash
    clean_shell_history

    echo
    echo -e "${COLOR_GREEN}=====================================================${COLOR_RESET}"
    if [[ "${DRY_RUN}" == true ]]; then
        echo -e "${COLOR_YELLOW}     SIMULAÇÃO CONCLUÍDA (--dry-run)                 ${COLOR_RESET}"
        echo -e "${COLOR_YELLOW}  Nenhum arquivo ou dado real foi modificado.        ${COLOR_RESET}"
    else
        echo -e "${COLOR_GREEN}     PROTOCOLO CONCLUÍDO COM SUCESSO!                ${COLOR_RESET}"
        echo -e "${COLOR_GREEN}  Recomenda-se fechar este terminal ou fazer logout. ${COLOR_RESET}"
    fi
    echo -e "${COLOR_GREEN}=====================================================${COLOR_RESET}"
}
```

Atualizar o ponto de entrada no final do script:
```bash
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    check_not_root
    parse_args "$@"
    confirm_execution
    run_protocol
fi
```

- [ ] **Step 4: Executar teste e verificar aprovação**

Run: `tests/test_user_and_custom.sh`
Expected: PASS com "Teste de Pastas de Usuário e Custom Paths passou com sucesso!"

- [ ] **Step 5: Commit**

```bash
git add protocolo-demissao.sh tests/test_user_and_custom.sh
git commit -m "feat: add user dirs, communication, IDEs, custom paths, trash, and history cleanup"
```

---

### Task 5: Consolidação dos Testes (E2E), Suíte Geral e Documentação (README)

**Files:**
- Create: `tests/run_all_tests.sh`
- Create: `README.md`

**Interfaces:**
- Produces:
  - `tests/run_all_tests.sh`: executa todos os testes unitários e de integração (`test_safety.sh`, `test_browsers.sh`, `test_credentials.sh`, `test_user_and_custom.sh`).
  - `README.md`: guia de uso em português, explicando pré-requisitos, personalização de `CUSTOM_PATHS`, uso do `--dry-run`, exemplos práticos e checklist de saída.

- [ ] **Step 1: Criar o script consolidado de testes `tests/run_all_tests.sh`**

```bash
cat << 'EOF' > tests/run_all_tests.sh
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Executando suíte completa de testes do Protocolo de Demissão..."
echo "---------------------------------------------------------------"

"${SCRIPT_DIR}/test_safety.sh"
"${SCRIPT_DIR}/test_browsers.sh"
"${SCRIPT_DIR}/test_credentials.sh"
"${SCRIPT_DIR}/test_user_and_custom.sh"

echo "---------------------------------------------------------------"
echo "TODOS OS TESTES PASSARAM COM SUCESSO!"
EOF
chmod +x tests/run_all_tests.sh
```

- [ ] **Step 2: Executar a suíte de testes e confirmar que todos passam**

Run: `tests/run_all_tests.sh`
Expected: PASS com "TODOS OS TESTES PASSARAM COM SUCESSO!"

- [ ] **Step 3: Criar documentação completa em `README.md`**

Escrever `README.md` com:
- Explicação do objetivo do script.
- Como configurar as variáveis no topo de `protocolo-demissao.sh`.
- Como adicionar diretórios no array `CUSTOM_PATHS`.
- Como rodar em modo simulação (`./protocolo-demissao.sh --dry-run`).
- Como rodar para execução real com a palavra de segurança `CONFIRMAR`.
- Mapeamento completo do que cada módulo limpa.

- [ ] **Step 4: Commit final**

```bash
git add tests/run_all_tests.sh README.md
git commit -m "docs: add comprehensive README and test suite runner"
```
