// src/utils/utils.js

export function normalizeConnections(arr) {
  return (arr || []).map((b) => ({
    id: b.id ?? b.bankid ?? undefined,
    provider: b.provider ?? "",
    bankaccount: b.bankaccount ?? "",
    bankpassword: b.bankpassword ?? "",
    bankid: b.bankid ?? "",
    last_update: b.last_update ?? null,
    account_name: b.account_name ?? "",
    BcCash: b.BcCash ?? null,
    BcMainaccount: b.BcMainaccount ?? null,
    BcStock: b.BcStock ?? null
  }));
}

export function maskAccount(acc) {
  if (!acc) return "(no account)";
  const s = String(acc).replace(/[^0-9A-Za-z]/g, "");
  const tail = s.slice(-4);
  return `•••• ${tail}`;
}

export function getProviderInitial(p) {
  if (!p) return "?";
  const word = String(p).replace(/[^A-Za-z]/g, " ").trim().split(" ")[0] || "?";
  return word[0].toUpperCase();
}

export function formatTime(ts) {
  if (!ts) return "";
  const d = new Date(ts);
  if (isNaN(d.getTime())) return String(ts);
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

export function formatCurrencyTWD(val) {
  const n = Number(val);
  if (!isFinite(n)) return String(val ?? "");
  try {
    return new Intl.NumberFormat("zh-TW", { style: "decimal", maximumFractionDigits: 0 }).format(n);
  } catch {
    return String(val);
  }
}

export function formatTimeLocalTPE(ts) {
  try {
    const d = new Date(ts);
    if (isNaN(d.getTime())) return String(ts);
    const parts = new Intl.DateTimeFormat("zh-TW", {
      timeZone: "Asia/Taipei",
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    })
      .formatToParts(d)
      .reduce((acc, p) => {
        acc[p.type] = p.value; 
        return acc;
      }, {});
    return `${parts.year}-${parts.month}-${parts.day} ${parts.hour}:${parts.minute}`;
  } catch {
    return String(ts ?? "");
  }
}

export const BANK_LOGOS = {
  LINE_BANK: "/logo/LINEBANK.png",
  CATHAY_BANK: "/logo/CATHAYBANK.png",
  ESUN_BANK: "/logo/ESUNBANK.png",
  CH_BANK: "/logo/CHBANK.png"
};

export function getBankLogoSrc(provider) {
  const key = String(provider || "").toUpperCase();
  return BANK_LOGOS[key] || null;
}

export const PROVIDER_LABELS = {
  LINE_BANK: "LINE Bank",
  CATHAY_BANK: "CATHAY Bank",
  ESUN_BANK: "ESUN Bank",
  CH_BANK: "CH Bank"
};

export function labelOf(p) {
  const key = String(p || "").toUpperCase();
  return PROVIDER_LABELS[key] || String(p || "").toUpperCase();
}
