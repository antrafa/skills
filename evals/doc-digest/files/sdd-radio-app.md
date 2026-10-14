# Software Design Document (SDD) - Aplicativo Mobile Rádio Nova Mensagem
**Versão:** 1.0.0  
**Data:** 17 de Setembro de 2026  
**Status:** Proposta Técnica para Validação  
**Identificador Alvo:** `radio.nova.mensagem.app`

---

## 1. Visão Geral e Arquitetura do Sistema

O objetivo deste projeto é substituir o aplicativo móvel existente da Rádio Nova Mensagem por uma solução moderna, mantendo a compatibilidade de distribuição na Google Play Store (`radio.nova.mensagem.app`). O app deve rodar streaming contínuo de áudio em segundo plano e exibir publicidades gerenciadas dinamicamente via painel administrativo do site (Payload CMS 3 + Next.js 16).

### 1.1 Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────────────────────┐
│              BACKEND / CMS (nova-mensagem-2026 - Next.js 16)            │
│                                                                         │
│  ┌─────────────────────────┐         ┌───────────────────────────────┐  │
│  │   Collection Parceiros  │         │   Global ConfiguracaoRadio    │  │
│  │  (Banners, Links, Prazos)│        │   (Stream URL, Status Rádio)  │  │
│  └───────────┬─────────────┘         └───────────────┬───────────────┘  │
│              │                                       │                  │
│              ▼                                       ▼                  │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │        API Gateway / Endpoints Públicos (/api/app/*)              │  │
│  │   - GET /api/app/config (URL stream, status, versão mínima)       │  │
│  │   - GET /api/app/publicidades (Banners ativos, posições, links)   │  │
│  └───────────────────────────────────┬───────────────────────────────┘  │
└──────────────────────────────────────┼──────────────────────────────────┘
                                       │ HTTPS / JSON
                                       ▼
┌─────────────────────────────────────────────────────────────────────────┐
│             APLICATIVO MOBILE (nova-mensagem-app - React Native)         │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                         UI Layer (Telas)                          │  │
│  │  - Player Principal (Botão Play/Pause, Estado de Buffer, Onda)   │  │
│  │  - Carrossel / Card de Publicidade Dinâmica (Parceiros Locais)    │  │
│  │  - Ações Rápidas (WhatsApp do Estúdio, Redes Sociais)             │  │
│  └───────────────────────────────────┬───────────────────────────────┘  │
│                                      │                                  │
│  ┌───────────────────────────────────▼───────────────────────────────┐  │
│  │                    Core de Áudio & Resiliência                    │  │
│  │  - react-native-track-player (Engine de Áudio Nativo)             │  │
│  │  - Foreground Service (FOREGROUND_SERVICE_MEDIA_PLAYBACK)         │  │
│  │  - MediaSession & Notificação Nativa (Lockscreen / Barra Status) │  │
│  │  - Audio Focus Manager (Pausa em chamadas, ducking em avisos)     │  │
│  │  - Reconnection Strategy (Exponential Backoff em perda de rede)   │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Decisões Tecnológicas e Justificativas

| Componente | Tecnologia Escolhida | Justificativa Técnica |
| :--- | :--- | :--- |
| **Framework Mobile** | **React Native (Expo bare / Prebuild)** | Compartilhamento do ecossistema TypeScript com o site; tipagem direta do `payload-types.ts`; performance nativa superior para streaming contínuo. |
| **Engine de Áudio** | **`react-native-track-player`** | Padrão da indústria para áudio em background. Implementa nativamente `MediaBrowserServiceCompat` no Android e `MPRemoteCommandCenter` no iOS, cumprindo 100% dos requisitos de `Foreground Service` da Google Play. |
| **Backend / CMS** | **Payload CMS 3 (PostgreSQL)** | Já em operação no projeto web (`nova-mensagem-2026`). Elimina a necessidade de criar servidores ou bancos de dados adicionais para gerenciar os anúncios e metadados. |
| **Estilização Mobile** | **Tailwind / StyleSheet** | Consistência visual e performance sem overhead de renderização. |

---

## 3. Especificação do Backend (Entrega 2)

### 3.1 Ponto Crítico Atual no Payload CMS
Atualmente, no projeto `nova-mensagem-2026`:
1. O global `ConfiguracaoRadio` possui `access: { read: authenticated }`. Clientes móveis sem login não conseguem ler a `streamURL`.
2. A collection `Parceiros` possui campos simples (`titulo`, `imagem`, `link`, `ativo`), mas não possui:
   - Ordenação prioritária (`ordem`).
   - Diferenciação de posicionamento (ex: banner topo, card rodapé).
   - Data limite de veiculação (`validoAte`).

### 3.2 Modificações e Novos Endpoints

#### Endpoint 1: Configuração do Aplicativo
- **Rota:** `GET /api/app/config`
- **Acesso:** Público (cacheado com `revalidateTag`)
- **Contrato de Resposta:**
```json
{
  "streamUrl": "https://stm1.painelstream.net:7000/stream",
  "status": "online",
  "tituloRadio": "Rádio Nova Mensagem",
  "slogan": "A voz da nossa gente",
  "whatsapp": "5511999999999",
  "versaoMinimaApp": "1.0.0"
}
```

#### Endpoint 2: Publicidades e Parceiros
- **Rota:** `GET /api/app/publicidades`
- **Acesso:** Público (`ativo: true` e `validoAte >= hoje`)
- **Contrato de Resposta:**
```json
{
  "docs": [
    {
      "id": "parceiro-1",
      "titulo": "Supermercado Central",
      "imagemUrl": "https://novamensagem.com.br/media/banner-app-supermercado.webp",
      "linkDestino": "https://wa.me/55...",
      "tipoAcao": "whatsapp",
      "ordem": 1
    }
  ]
}
```

---

## 4. Especificação do Core Mobile (Entrega 3)

### 4.1 Ciclo de Vida do Áudio e Foreground Service
O aplicativo deve declarar no `AndroidManifest.xml`:
- `android.permission.FOREGROUND_SERVICE`
- `android.permission.FOREGROUND_SERVICE_MEDIA_PLAYBACK`
- `android.permission.WAKE_LOCK`

O serviço de áudio deve ser iniciado com notificação persistente contendo:
- Nome da rádio ("Rádio Nova Mensagem").
- Estado atual ("Ao vivo", "Conectando...", "Pausado").
- Ação interativa direta: Botão Play/Pause.

### 4.2 Tratamento de Conexão e Foco de Áudio (Audio Focus)
- **Chamada Telefônica:** O app deve pausar imediatamente ao receber `AUDIOFOCUS_LOSS_TRANSIENT` e retomar quando a chamada terminar.
- **Notificações do Sistema:** Deve executar "ducking" (redução de 80% no volume por 2 segundos) sem interromper a transmissão.
- **Queda de Conexão (3G -> Wi-Fi -> Sem Rede):** O player deve entrar em estado `buffering`, tentando reconectar em intervalos de 1s, 3s, 5s e 10s (Exponential Backoff). Caso a conexão falhe por mais de 30 segundos, o player entra em estado `idle` com aviso amigável na tela ("Toque para tentar novamente").

---

## 5. Especificação do Módulo de Publicidade (Entrega 4)

### 5.1 Apresentação Visual dos Anúncios
- **Posicionamento:** Slot dinâmico logo abaixo do Player Principal.
- **Comportamento:** Carrossel rotativo automático (a cada 7 segundos) ou banner fixo com suporte a swipe.
- **Abertura Segura de Links:** 
  - URLs web são abertas no navegador do sistema (`Linking.openURL`).
  - Links com protocolo `whatsapp://` ou números de telefone acionam o intent nativo do aplicativo correspondente.

### 5.2 Resiliência Offline
Caso o usuário abra o app em um túnel ou sem internet:
- O app armazena a última lista de parceiros em cache local (`AsyncStorage`).
- Exibe o anúncio cacheado sem quebrar a interface.

---

## 6. Matriz de Riscos e Bloqueadores

| Risco | Impacto | Mitigação Técnica |
| :--- | :--- | :--- |
| **Atraso na Entrega 1 (Chaves/Google Play)** | Alto para lançamento, nulo para código | Desenvolver todo o app com package `radio.nova.mensagem.app`. Caso a conta seja negada, altera-se apenas o `app.json` / `build.gradle` para o novo namespace em minutos. |
| **Reprovação na Google Play (Foreground Service)** | Alto | Implementar estritamente o `MediaSession` compatível com Android 14/15 e preparar vídeo de teste gravando a tela do celular com o som tocando de tela apagada. |
| **Consumo Excessivo de Dados do Usuário** | Médio | Configurar buffer otimizado no ExoPlayer nativo para transmissões AAC/MP3 de baixo bitrate (64k-128kbps). |
