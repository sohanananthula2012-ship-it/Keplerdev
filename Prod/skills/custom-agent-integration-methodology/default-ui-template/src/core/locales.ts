import type { BuilderPublicSiteLocale, BuilderPublicSiteLocaleInput } from './types';

export const BUILDER_PUBLIC_SITE_LANGUAGE_DEFINITIONS = [
  { language: 'en', label: 'English', detectionPrefixes: ['en'] },
  { language: 'zh-CN', label: '简体中文', detectionPrefixes: ['zh'] },
  { language: 'de-DE', label: 'Deutsch', detectionPrefixes: ['de'] },
  { language: 'pt-BR', label: 'Português (Brasil)', detectionPrefixes: ['pt'] },
  { language: 'es-ES', label: 'Español', detectionPrefixes: ['es'] },
  { language: 'fr-FR', label: 'Français', detectionPrefixes: ['fr'] },
  { language: 'id-ID', label: 'Bahasa Indonesia', detectionPrefixes: ['id'] },
  { language: 'it-IT', label: 'Italiano', detectionPrefixes: ['it'] },
  { language: 'ja-JP', label: '日本語', detectionPrefixes: ['ja'] },
  { language: 'ko-KR', label: '한국어', detectionPrefixes: ['ko'] },
  { language: 'ru-RU', label: 'Русский', detectionPrefixes: ['ru'] },
  { language: 'ar-SA', label: 'العربية', detectionPrefixes: ['ar'] },
  { language: 'tr-TR', label: 'Türkçe', detectionPrefixes: ['tr'] },
] as const satisfies readonly {
  language: BuilderPublicSiteLocale;
  label: string;
  detectionPrefixes: readonly string[];
}[];

export const BUILDER_PUBLIC_SITE_SUPPORTED_LOCALES = BUILDER_PUBLIC_SITE_LANGUAGE_DEFINITIONS.map(
  ({ language }) => language,
) as readonly BuilderPublicSiteLocale[];

export const BUILDER_PUBLIC_SITE_LANGUAGE_LABELS = Object.fromEntries(
  BUILDER_PUBLIC_SITE_LANGUAGE_DEFINITIONS.map(({ language, label }) => [language, label]),
) as Record<BuilderPublicSiteLocale, string>;

export const DEFAULT_BUILDER_PUBLIC_SITE_LOCALE: BuilderPublicSiteLocale = 'zh-CN';
export const FALLBACK_BUILDER_PUBLIC_SITE_LOCALE: BuilderPublicSiteLocale = 'en';

const LANGUAGE_PREFIX_FALLBACKS = BUILDER_PUBLIC_SITE_LANGUAGE_DEFINITIONS.flatMap(
  ({ language, detectionPrefixes }) => detectionPrefixes.map((prefix) => [prefix, language] as const),
);

type NavigatorLike = {
  language?: string;
  languages?: readonly string[];
};

export type BuilderPublicSiteLabels = {
  agentReady: string;
  agentRunning: string;
  startupEnvPreparing: string;
  startupEnvPrepared: string;
  startupConfigLoading: string;
  startupConfigLoaded: string;
  startupResponding: string;
  startupResponded: string;
  agentCancelled: string;
  agentError: string;
  thinkingStreaming: string;
  thinkingDone: (seconds: number) => string;
  actionsStreaming: (count: number) => string;
  actionsDone: (count: number) => string;
  actionsError: (count: number) => string;
  send: string;
  placeholder: string;
  newSession: string;
  emptyTitle: string;
  retry: string;
  reconnect: string;
  stop: string;
  debugUnsupported: string;
  defaultError: string;
  cancelled: string;
  outOfCredit: string;
};

function plural(count: number, one: string, many = `${one}s`) {
  return count === 1 ? one : many;
}

export const labels: Record<BuilderPublicSiteLocale, BuilderPublicSiteLabels> = {
  'zh-CN': {
    agentReady: 'Agent 就绪',
    agentRunning: 'Agent 准备中...',
    startupEnvPreparing: 'Agent 环境准备中',
    startupEnvPrepared: 'Agent 环境已准备',
    startupConfigLoading: 'Agent 配置加载中',
    startupConfigLoaded: 'Agent 配置已加载',
    startupResponding: 'Agent 响应中...',
    startupResponded: 'Agent 已响应',
    agentCancelled: '已取消',
    agentError: '运行失败',
    thinkingStreaming: '思考中',
    thinkingDone: (seconds) => `思考了 ${seconds} 秒`,
    actionsStreaming: (count) => `正在执行 ${count} 个操作`,
    actionsDone: (count) => `已完成 ${count} 个操作`,
    actionsError: (count) => `${count} 个操作失败`,
    send: '发送',
    placeholder: '输入消息...',
    newSession: '新会话',
    emptyTitle: '新会话',
    retry: '重试',
    reconnect: '重连',
    stop: '停止',
    debugUnsupported: '未支持事件',
    defaultError: 'Agent 运行失败，请稍后重试。',
    cancelled: '本次运行已取消。',
    outOfCredit: '额度不足。',
  },
  en: {
    agentReady: 'Agent ready',
    agentRunning: 'Agent is preparing...',
    startupEnvPreparing: 'Agent environment preparing',
    startupEnvPrepared: 'Agent environment prepared',
    startupConfigLoading: 'Agent config loading',
    startupConfigLoaded: 'Agent config loaded',
    startupResponding: 'Agent responding...',
    startupResponded: 'Agent responded',
    agentCancelled: 'Cancelled',
    agentError: 'Run failed',
    thinkingStreaming: 'Thinking',
    thinkingDone: (seconds) => `Thought for ${seconds}s`,
    actionsStreaming: (count) => `Running ${count} ${plural(count, 'action')}`,
    actionsDone: (count) => `Completed ${count} ${plural(count, 'action')}`,
    actionsError: (count) => `${count} ${plural(count, 'action')} failed`,
    send: 'Send',
    placeholder: 'Message...',
    newSession: 'New session',
    emptyTitle: 'New Session',
    retry: 'Retry',
    reconnect: 'Reconnect',
    stop: 'Stop',
    debugUnsupported: 'Unsupported event',
    defaultError: 'The agent run failed. Please try again.',
    cancelled: 'This run was cancelled.',
    outOfCredit: 'Out of credit.',
  },
  'de-DE': {
    agentReady: 'Agent bereit',
    agentRunning: 'Agent wird vorbereitet',
    startupEnvPreparing: 'Umgebung wird vorbereitet',
    startupEnvPrepared: 'Umgebung bereit',
    startupConfigLoading: 'Agent-Konfiguration wird geladen',
    startupConfigLoaded: 'Agent-Konfiguration geladen',
    startupResponding: 'Warte auf Agent-Antwort',
    startupResponded: 'Agent hat geantwortet',
    agentCancelled: 'Abgebrochen',
    agentError: 'Ausführung fehlgeschlagen',
    thinkingStreaming: 'Denke nach',
    thinkingDone: (seconds) => `${seconds}s nachgedacht`,
    actionsStreaming: (count) => `${count} ${plural(count, 'Aktion', 'Aktionen')} läuft`,
    actionsDone: (count) => `${count} ${plural(count, 'Aktion', 'Aktionen')} abgeschlossen`,
    actionsError: (count) => `${count} ${plural(count, 'Aktion', 'Aktionen')} fehlgeschlagen`,
    send: 'Senden',
    placeholder: 'Nachricht...',
    newSession: 'Neue Sitzung',
    emptyTitle: 'Neue Sitzung',
    retry: 'Erneut versuchen',
    reconnect: 'Neu verbinden',
    stop: 'Stopp',
    debugUnsupported: 'Nicht unterstütztes Ereignis',
    defaultError: 'Die Agent-Ausführung ist fehlgeschlagen. Bitte versuchen Sie es erneut.',
    cancelled: 'Diese Ausführung wurde abgebrochen.',
    outOfCredit: 'Guthaben aufgebraucht.',
  },
  'pt-BR': {
    agentReady: 'Agente pronto',
    agentRunning: 'Agente se preparando',
    startupEnvPreparing: 'Preparando ambiente',
    startupEnvPrepared: 'Ambiente pronto',
    startupConfigLoading: 'Carregando configuração do agente',
    startupConfigLoaded: 'Configuração do agente carregada',
    startupResponding: 'Aguardando resposta do agente',
    startupResponded: 'Agente respondeu',
    agentCancelled: 'Cancelado',
    agentError: 'Execução falhou',
    thinkingStreaming: 'Pensando',
    thinkingDone: (seconds) => `Pensou por ${seconds}s`,
    actionsStreaming: (count) => `Executando ${count} ${plural(count, 'ação', 'ações')}`,
    actionsDone: (count) => `${count} ${plural(count, 'ação concluída', 'ações concluídas')}`,
    actionsError: (count) => `${count} ${plural(count, 'ação falhou', 'ações falharam')}`,
    send: 'Enviar',
    placeholder: 'Mensagem...',
    newSession: 'Nova sessão',
    emptyTitle: 'Nova sessão',
    retry: 'Tentar novamente',
    reconnect: 'Reconectar',
    stop: 'Parar',
    debugUnsupported: 'Evento não suportado',
    defaultError: 'A execução do agente falhou. Tente novamente.',
    cancelled: 'Esta execução foi cancelada.',
    outOfCredit: 'Créditos insuficientes.',
  },
  'es-ES': {
    agentReady: 'Agente listo',
    agentRunning: 'Agente preparándose',
    startupEnvPreparing: 'Preparando entorno',
    startupEnvPrepared: 'Entorno listo',
    startupConfigLoading: 'Cargando configuración del agente',
    startupConfigLoaded: 'Configuración del agente cargada',
    startupResponding: 'Esperando respuesta del agente',
    startupResponded: 'El agente respondió',
    agentCancelled: 'Cancelado',
    agentError: 'La ejecución falló',
    thinkingStreaming: 'Pensando',
    thinkingDone: (seconds) => `Pensó durante ${seconds}s`,
    actionsStreaming: (count) => `Ejecutando ${count} ${plural(count, 'acción', 'acciones')}`,
    actionsDone: (count) => `${count} ${plural(count, 'acción completada', 'acciones completadas')}`,
    actionsError: (count) => `${count} ${plural(count, 'acción falló', 'acciones fallaron')}`,
    send: 'Enviar',
    placeholder: 'Mensaje...',
    newSession: 'Nueva sesión',
    emptyTitle: 'Nueva sesión',
    retry: 'Reintentar',
    reconnect: 'Reconectar',
    stop: 'Detener',
    debugUnsupported: 'Evento no compatible',
    defaultError: 'La ejecución del agente falló. Inténtalo de nuevo.',
    cancelled: 'Esta ejecución fue cancelada.',
    outOfCredit: 'Sin crédito.',
  },
  'fr-FR': {
    agentReady: 'Agent prêt',
    agentRunning: 'Agent en préparation',
    startupEnvPreparing: "Préparation de l'environnement",
    startupEnvPrepared: 'Environnement prêt',
    startupConfigLoading: "Chargement de la configuration de l'agent",
    startupConfigLoaded: "Configuration de l'agent chargée",
    startupResponding: "En attente de la réponse de l'agent",
    startupResponded: "L'agent a répondu",
    agentCancelled: 'Annulé',
    agentError: "L'exécution a échoué",
    thinkingStreaming: 'Réflexion en cours',
    thinkingDone: (seconds) => `Réflexion pendant ${seconds}s`,
    actionsStreaming: (count) => `${count} ${plural(count, 'action en cours', 'actions en cours')}`,
    actionsDone: (count) => `${count} ${plural(count, 'action terminée', 'actions terminées')}`,
    actionsError: (count) => `${count} ${plural(count, 'action a échoué', 'actions ont échoué')}`,
    send: 'Envoyer',
    placeholder: 'Message...',
    newSession: 'Nouvelle session',
    emptyTitle: 'Nouvelle session',
    retry: 'Réessayer',
    reconnect: 'Reconnecter',
    stop: 'Arrêter',
    debugUnsupported: 'Événement non pris en charge',
    defaultError: "L'exécution de l'agent a échoué. Veuillez réessayer.",
    cancelled: 'Cette exécution a été annulée.',
    outOfCredit: 'Crédit épuisé.',
  },
  'id-ID': {
    agentReady: 'Agent siap',
    agentRunning: 'Agent sedang bersiap',
    startupEnvPreparing: 'Menyiapkan lingkungan',
    startupEnvPrepared: 'Lingkungan siap',
    startupConfigLoading: 'Memuat konfigurasi agent',
    startupConfigLoaded: 'Konfigurasi agent dimuat',
    startupResponding: 'Menunggu respons agent',
    startupResponded: 'Agent merespons',
    agentCancelled: 'Dibatalkan',
    agentError: 'Eksekusi gagal',
    thinkingStreaming: 'Berpikir',
    thinkingDone: (seconds) => `Berpikir selama ${seconds}d`,
    actionsStreaming: (count) => `Menjalankan ${count} aksi`,
    actionsDone: (count) => `${count} aksi selesai`,
    actionsError: (count) => `${count} aksi gagal`,
    send: 'Kirim',
    placeholder: 'Pesan...',
    newSession: 'Sesi baru',
    emptyTitle: 'Sesi baru',
    retry: 'Coba lagi',
    reconnect: 'Hubungkan ulang',
    stop: 'Berhenti',
    debugUnsupported: 'Event tidak didukung',
    defaultError: 'Eksekusi agent gagal. Silakan coba lagi.',
    cancelled: 'Eksekusi ini dibatalkan.',
    outOfCredit: 'Kredit habis.',
  },
  'it-IT': {
    agentReady: 'Agente pronto',
    agentRunning: 'Agente in preparazione',
    startupEnvPreparing: "Preparazione dell'ambiente",
    startupEnvPrepared: 'Ambiente pronto',
    startupConfigLoading: "Caricamento configurazione dell'agente",
    startupConfigLoaded: "Configurazione dell'agente caricata",
    startupResponding: "In attesa della risposta dell'agente",
    startupResponded: "L'agente ha risposto",
    agentCancelled: 'Annullato',
    agentError: 'Esecuzione non riuscita',
    thinkingStreaming: 'Ragionamento in corso',
    thinkingDone: (seconds) => `Ha ragionato per ${seconds}s`,
    actionsStreaming: (count) => `Esecuzione di ${count} ${plural(count, 'azione', 'azioni')}`,
    actionsDone: (count) => `${count} ${plural(count, 'azione completata', 'azioni completate')}`,
    actionsError: (count) => `${count} ${plural(count, 'azione non riuscita', 'azioni non riuscite')}`,
    send: 'Invia',
    placeholder: 'Messaggio...',
    newSession: 'Nuova sessione',
    emptyTitle: 'Nuova sessione',
    retry: 'Riprova',
    reconnect: 'Riconnetti',
    stop: 'Ferma',
    debugUnsupported: 'Evento non supportato',
    defaultError: "L'esecuzione dell'agente non è riuscita. Riprova.",
    cancelled: 'Questa esecuzione è stata annullata.',
    outOfCredit: 'Credito esaurito.',
  },
  'ja-JP': {
    agentReady: 'Agent 準備完了',
    agentRunning: 'Agent 準備中',
    startupEnvPreparing: '環境を準備中',
    startupEnvPrepared: '環境の準備完了',
    startupConfigLoading: 'agent 設定を読み込み中',
    startupConfigLoaded: 'agent 設定を読み込みました',
    startupResponding: 'agent の応答を待機中',
    startupResponded: 'agent が応答しました',
    agentCancelled: 'キャンセル済み',
    agentError: '実行に失敗しました',
    thinkingStreaming: '思考中',
    thinkingDone: (seconds) => `${seconds} 秒考えました`,
    actionsStreaming: (count) => `${count} 件の操作を実行中`,
    actionsDone: (count) => `${count} 件の操作が完了`,
    actionsError: (count) => `${count} 件の操作に失敗`,
    send: '送信',
    placeholder: 'メッセージを入力...',
    newSession: '新しいセッション',
    emptyTitle: '新しいセッション',
    retry: '再試行',
    reconnect: '再接続',
    stop: '停止',
    debugUnsupported: '未対応イベント',
    defaultError: 'Agent の実行に失敗しました。もう一度お試しください。',
    cancelled: 'この実行はキャンセルされました。',
    outOfCredit: 'クレジット不足です。',
  },
  'ko-KR': {
    agentReady: 'Agent 준비됨',
    agentRunning: 'Agent 준비 중',
    startupEnvPreparing: '환경 준비 중',
    startupEnvPrepared: '환경 준비됨',
    startupConfigLoading: 'agent 설정 로드 중',
    startupConfigLoaded: 'agent 설정 로드됨',
    startupResponding: 'agent 응답 대기 중',
    startupResponded: 'agent가 응답함',
    agentCancelled: '취소됨',
    agentError: '실행 실패',
    thinkingStreaming: '생각 중',
    thinkingDone: (seconds) => `${seconds}초 동안 생각함`,
    actionsStreaming: (count) => `${count}개 작업 실행 중`,
    actionsDone: (count) => `${count}개 작업 완료`,
    actionsError: (count) => `${count}개 작업 실패`,
    send: '보내기',
    placeholder: '메시지 입력...',
    newSession: '새 세션',
    emptyTitle: '새 세션',
    retry: '다시 시도',
    reconnect: '다시 연결',
    stop: '중지',
    debugUnsupported: '지원되지 않는 이벤트',
    defaultError: 'Agent 실행에 실패했습니다. 다시 시도해 주세요.',
    cancelled: '이 실행은 취소되었습니다.',
    outOfCredit: '크레딧이 부족합니다.',
  },
  'ru-RU': {
    agentReady: 'Agent готов',
    agentRunning: 'Agent готовится',
    startupEnvPreparing: 'Подготовка окружения',
    startupEnvPrepared: 'Окружение готово',
    startupConfigLoading: 'Загрузка конфигурации agent',
    startupConfigLoaded: 'Конфигурация agent загружена',
    startupResponding: 'Ожидание ответа agent',
    startupResponded: 'Agent ответил',
    agentCancelled: 'Отменено',
    agentError: 'Запуск не удался',
    thinkingStreaming: 'Думает',
    thinkingDone: (seconds) => `Думал ${seconds} с`,
    actionsStreaming: (count) => `Выполняется ${count} действ.`,
    actionsDone: (count) => `Завершено ${count} действ.`,
    actionsError: (count) => `Не удалось ${count} действ.`,
    send: 'Отправить',
    placeholder: 'Сообщение...',
    newSession: 'Новая сессия',
    emptyTitle: 'Новая сессия',
    retry: 'Повторить',
    reconnect: 'Переподключиться',
    stop: 'Остановить',
    debugUnsupported: 'Неподдерживаемое событие',
    defaultError: 'Запуск agent не удался. Повторите попытку.',
    cancelled: 'Этот запуск был отменен.',
    outOfCredit: 'Недостаточно кредитов.',
  },
  'ar-SA': {
    agentReady: 'الوكيل جاهز',
    agentRunning: 'الوكيل يستعد',
    startupEnvPreparing: 'جار تجهيز البيئة',
    startupEnvPrepared: 'البيئة جاهزة',
    startupConfigLoading: 'جار تحميل إعدادات الوكيل',
    startupConfigLoaded: 'تم تحميل إعدادات الوكيل',
    startupResponding: 'بانتظار رد الوكيل',
    startupResponded: 'رد الوكيل',
    agentCancelled: 'تم الإلغاء',
    agentError: 'فشل التشغيل',
    thinkingStreaming: 'يفكر',
    thinkingDone: (seconds) => `فكر لمدة ${seconds} ث`,
    actionsStreaming: (count) => `جار تنفيذ ${count} إجراء`,
    actionsDone: (count) => `اكتمل ${count} إجراء`,
    actionsError: (count) => `فشل ${count} إجراء`,
    send: 'إرسال',
    placeholder: 'رسالة...',
    newSession: 'جلسة جديدة',
    emptyTitle: 'جلسة جديدة',
    retry: 'إعادة المحاولة',
    reconnect: 'إعادة الاتصال',
    stop: 'إيقاف',
    debugUnsupported: 'حدث غير مدعوم',
    defaultError: 'فشل تشغيل الوكيل. يرجى المحاولة مرة أخرى.',
    cancelled: 'تم إلغاء هذا التشغيل.',
    outOfCredit: 'الرصيد غير كاف.',
  },
  'tr-TR': {
    agentReady: 'Agent hazır',
    agentRunning: 'Agent hazırlanıyor',
    startupEnvPreparing: 'Ortam hazırlanıyor',
    startupEnvPrepared: 'Ortam hazır',
    startupConfigLoading: 'Agent yapılandırması yükleniyor',
    startupConfigLoaded: 'Agent yapılandırması yüklendi',
    startupResponding: 'Agent yanıtı bekleniyor',
    startupResponded: 'Agent yanıt verdi',
    agentCancelled: 'İptal edildi',
    agentError: 'Çalıştırma başarısız',
    thinkingStreaming: 'Düşünüyor',
    thinkingDone: (seconds) => `${seconds} sn düşündü`,
    actionsStreaming: (count) => `${count} işlem çalışıyor`,
    actionsDone: (count) => `${count} işlem tamamlandı`,
    actionsError: (count) => `${count} işlem başarısız`,
    send: 'Gönder',
    placeholder: 'Mesaj...',
    newSession: 'Yeni oturum',
    emptyTitle: 'Yeni oturum',
    retry: 'Yeniden dene',
    reconnect: 'Yeniden bağlan',
    stop: 'Durdur',
    debugUnsupported: 'Desteklenmeyen olay',
    defaultError: 'Agent çalıştırması başarısız oldu. Lütfen tekrar deneyin.',
    cancelled: 'Bu çalıştırma iptal edildi.',
    outOfCredit: 'Kredi yetersiz.',
  },
};

export function normalizeBuilderPublicSiteLocale(value: BuilderPublicSiteLocaleInput | null | undefined): BuilderPublicSiteLocale | null {
  if (!value) return null;
  const trimmedValue = String(value).trim();
  if (!trimmedValue) return null;
  if (trimmedValue === 'zh') return 'zh-CN';

  const exactMatch = BUILDER_PUBLIC_SITE_SUPPORTED_LOCALES.find((language) => language === trimmedValue);
  if (exactMatch) return exactMatch;

  const lowerCasedValue = trimmedValue.toLowerCase();
  const caseInsensitiveMatch = BUILDER_PUBLIC_SITE_SUPPORTED_LOCALES.find(
    (language) => language.toLowerCase() === lowerCasedValue,
  );
  if (caseInsensitiveMatch) return caseInsensitiveMatch;

  const prefixMatch = LANGUAGE_PREFIX_FALLBACKS.find(
    ([prefix]) => lowerCasedValue === prefix || lowerCasedValue.startsWith(`${prefix}-`),
  );
  return prefixMatch?.[1] ?? null;
}

export function detectBuilderPublicSiteNavigatorLocale(navigatorLike?: NavigatorLike): BuilderPublicSiteLocale | null {
  const languages = navigatorLike?.languages ?? [];
  for (const language of languages) {
    const normalized = normalizeBuilderPublicSiteLocale(language);
    if (normalized) return normalized;
  }
  return normalizeBuilderPublicSiteLocale(navigatorLike?.language);
}

export function resolveBuilderPublicSiteLocale(
  locale?: BuilderPublicSiteLocaleInput | null,
  fallbackLocale: BuilderPublicSiteLocale = DEFAULT_BUILDER_PUBLIC_SITE_LOCALE,
): BuilderPublicSiteLocale {
  return normalizeBuilderPublicSiteLocale(locale) ?? fallbackLocale;
}

export function resolvePreferredBuilderPublicSiteLocale(options?: {
  explicitLocale?: BuilderPublicSiteLocaleInput | null;
  cookieLocale?: BuilderPublicSiteLocaleInput | null;
  navigatorLike?: NavigatorLike;
  fallbackLocale?: BuilderPublicSiteLocale;
}): BuilderPublicSiteLocale {
  return (
    normalizeBuilderPublicSiteLocale(options?.explicitLocale) ??
    normalizeBuilderPublicSiteLocale(options?.cookieLocale) ??
    detectBuilderPublicSiteNavigatorLocale(
      options?.navigatorLike ?? (typeof navigator !== 'undefined' ? navigator : undefined),
    ) ??
    options?.fallbackLocale ??
    DEFAULT_BUILDER_PUBLIC_SITE_LOCALE
  );
}

export function localeLabels(locale?: BuilderPublicSiteLocaleInput | null) {
  const normalized = resolveBuilderPublicSiteLocale(locale);
  return labels[normalized] ?? labels[FALLBACK_BUILDER_PUBLIC_SITE_LOCALE];
}

export function localeTextDirection(locale?: BuilderPublicSiteLocaleInput | null) {
  return resolveBuilderPublicSiteLocale(locale) === 'ar-SA' ? 'rtl' : 'ltr';
}

export function questionCardLabels(locale?: BuilderPublicSiteLocaleInput | null) {
  const normalized = resolveBuilderPublicSiteLocale(locale);
  if (normalized === 'zh-CN') {
    return {
      questions: '问题',
      previousQuestion: '上一题',
      nextQuestion: '下一题',
      otherOption: '其他',
      otherPlaceholder: '其他...',
      skipRemaining: '跳过剩余',
      continue: '继续',
      submitting: '提交中...',
    };
  }
  return {
    questions: 'Questions',
    previousQuestion: 'Previous question',
    nextQuestion: 'Next question',
    otherOption: 'Other',
    otherPlaceholder: 'Other...',
    skipRemaining: 'Skip remaining',
    continue: 'Continue',
    submitting: 'Submitting...',
  };
}

export function secondsFromDuration(durationMs?: number) {
  if (!durationMs || durationMs <= 0) return 1;
  return Math.max(1, Math.round(durationMs / 1000));
}
