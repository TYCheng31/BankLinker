import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import styles from "./Dashboard.module.css";
import ConfirmDeleteModal from './ConfirmDeleteModal';

const versionNumber = "v1.1.1 250902";

function normalizeConnections(arr) {
  return (arr || []).map((b) => ({
    id: b.id ?? b.bankid ?? undefined,
    provider: b.provider ?? "",
    bankaccount: b.bankaccount ?? "",
    bankpassword: b.bankpassword ?? "",
    bankid: b.bankid ?? "",
    last_update: b.last_update ?? null,
  }));
}

(function test_normalizeConnections() {
  const a = normalizeConnections([{ id: "1", provider: "ESUN_BANK", bankaccount: "A", bankid: "X" }]);
  console.assert(a[0].id === "1", "id should be preserved");
  const b = normalizeConnections([{ bankid: "B2", provider: "LINE_BANK" }]);
  console.assert(b[0].id === "B2", "id should fallback to bankid");
  const c = normalizeConnections([{}]);
  console.assert(c[0].provider === "" && c[0].bankaccount === "", "defaults should be empty strings");
})();

function maskAccount(acc) {
  if (!acc) return "(no account)";
  const s = String(acc).replace(/[^0-9A-Za-z]/g, "");
  const tail = s.slice(-4);
  return `•••• ${tail}`;
}

function getProviderInitial(p) {
  if (!p) return "?";
  const word = String(p).replace(/[^A-Za-z]/g, " ").trim().split(" ")[0] || "?";
  return word[0].toUpperCase();
}

(function test_ui_helpers() {
  console.assert(maskAccount("12345678").endsWith("5678"), "maskAccount shows last 4");
  console.assert(maskAccount(0).includes("no account"), "maskAccount handles falsy");
  console.assert(getProviderInitial("ESUN_BANK") === "E", "initial from provider");
})();

function formatTime(ts) {
  if (!ts) return "";
  const d = new Date(ts);
  if (isNaN(d.getTime())) return String(ts);
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

(function test_formatTime() {
  const out = formatTime("2025-01-02T03:04:05Z");
  console.assert(/2025-0?1-0?2/.test(out), "formatTime date ok");
})();

function formatCurrencyTWD(val) {
  const n = Number(val);
  if (!isFinite(n)) return String(val ?? "");
  try {
    return new Intl.NumberFormat("zh-TW", { style: "currency", currency: "TWD", maximumFractionDigits: 0 }).format(n);
  } catch {
    return String(val);
  }
}

function formatTimeLocalTPE(ts) {
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
      .reduce((acc, p) => ((acc[p.type] = p.value), acc), {});
    return `${parts.year}-${parts.month}-${parts.day} ${parts.hour}:${parts.minute}`;
  } catch {
    return String(ts ?? "");
  }
}

(function test_formatters() {
  const c = formatCurrencyTWD(12345);
  console.assert(/12,?345/.test(c), "currency grouping ok");
  const t = formatTimeLocalTPE("2025-01-02T03:04:05Z");
  console.assert(/2025-0?1-0?2/.test(t), "TPE time formatted");
})();

const BANK_LOGOS = {
  LINE_BANK: "/logo/LINEBANK.png",
  CATHAY_BANK: "/logo/CATHAYBANK.png",
  ESUN_BANK: "/logo/ESUNBANK.png",
};

function getBankLogoSrc(provider) {
  const key = String(provider || "").toUpperCase();
  return BANK_LOGOS[key] || null;
}

const PROVIDER_LABELS = {
  LINE_BANK: "LINE Bank",
  CATHAY_BANK: "Cathay Bank",
  ESUN_BANK: "ESUN Bank",
};

function labelOf(p) {
  const key = String(p || "").toUpperCase();
  return PROVIDER_LABELS[key] || String(p || "").toUpperCase();
}
/* =======================
   Component
   ======================= */
const Dashboard = () => {
  const navigate = useNavigate();

  const [form, setForm] = useState({ bank_id: "", provider: "", account: "", password: ""});
  const [message, setMessage] = useState("");
  const [banks, setBanks] = useState([]);
  const [showAddContainer, setShowAddContainer] = useState(false);
  const [loading, setLoading] = useState(false);
  const [mainAccount, setMainAccount] = useState("");
  const [availableBalance, setAvailableBalance] = useState("");
  const [userAccount, setUserAccount] = useState("");
  const [userEmail, setUserEmail] = useState("");
  const [theme, setTheme] = useState("dark");       // 'dark' | 'light'
  const [lastUpdated, setLastUpdated] = useState(null);
  const [banner, setBanner] = useState(null);
  const [selectedBank, setSelectedBank] = useState(null); // 用來儲存當前選擇的銀行資料
  const [isModalOpen, setIsModalOpen] = useState(false); // 控制模態框的顯示與隱藏

  useEffect(() => {
    const token = sessionStorage.getItem("access_token");
    if (!token) {
      navigate("/login", { replace: true });
      return;
    }
    axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;

    const account = sessionStorage.getItem("user_account") || "";
    setUserAccount(account);

    const fetchUser = async () => {
      try {
        const res = await axios.get("/auth/me");
        setUserEmail(res.data.email || "");
      } catch (err) {
        console.error("Error fetching user info:", err);
      }
    };

    const fetchBanks = async () => {
      try {
        const response = await axios.get("/bank-connections");
        setBanks(normalizeConnections(response.data));
      } catch (err) {
        console.error("Error fetching bank connections:", err);
      }
    };

    fetchUser();
    fetchBanks();
  }, [navigate]);

  // init theme from localStorage or system preference; persist on change
  useEffect(() => {
    try {
      const saved = localStorage.getItem("theme");
      if (saved === "light" || saved === "dark") {
        setTheme(saved);
      } else if (window.matchMedia) {
        setTheme(window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
      }
    } catch {}
  }, []);
  useEffect(() => {
    try {
      localStorage.setItem("theme", theme);
    } catch {}
  }, [theme]);

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const payload = {
      provider: form.provider,
      bankaccount: form.account,
      bankid: form.bank_id,
      bankpassword: form.password,
    };

    try {
      const res = await axios.post("/bank-connections/", payload);
      setMessage("✅");
      setForm({ bank_id: "", provider: "", account: "", password: "" });
      setShowAddContainer(false);
      setBanner("已新增銀行連線");
      setTimeout(() => setBanner(null), 2000);

      const created = res?.data ?? payload;
      setBanks((prev) => [
        ...prev,
        {
          id: created.id ?? created.bankid ?? undefined,
          provider: created.provider ?? "",
          bankaccount: created.bankaccount ?? "",
          bankpassword: "",
          bankid: created.bankid ?? "",
        },
      ]);
    } catch (err) {
      console.error("submit error", err.response?.data || err.message);
      setMessage("❌");
    }
  };

  const handleLogout = async () => {
    try {
      // 若有登出 API 可呼叫；此處直接前端清理
    } finally {
      sessionStorage.removeItem("access_token");
      sessionStorage.removeItem("user_account");
      delete axios.defaults.headers.common["Authorization"];
      navigate("/login", { replace: true });
    }
  };

//################## 刪除bankCard ######################################################################

  const handleOpenModal = (bank) => {
    setSelectedBank(bank);
    setIsModalOpen(true);
  };

  const handleCancelDelete = () => {
    setIsModalOpen(false);
    setSelectedBank(null);
  };

  const handleConfirmDelete = async () => {
    if (!selectedBank) return;
    const { bankid, provider } = selectedBank;

    try {
      const encodedProvider = encodeURIComponent(provider);
      const encodedBankId   = encodeURIComponent(bankid);

      await axios.delete(`/bank-connections/${encodedProvider}/${encodedBankId}`);

      // 只刪除同一個 provider + bankid 的那一筆
      setBanks((prev) => prev.filter(x => !(x.bankid === bankid && x.provider === provider)));

      setBanner("Bank connection deleted.");
      setTimeout(() => setBanner(null), 2000);
    } catch (err) {
      console.error("Error deleting bank connection:", err);
      alert("Failed to delete bank connection.");
    } finally {
      setIsModalOpen(false);
      setSelectedBank(null);
    }
  };

  const toggleAddContainer = () => setShowAddContainer((v) => !v);

//########################## 爬蟲抓取各家銀行 ##########################################################
//
// LineBank、CathayBank、EsunBank
//
  const UpdateLinebank = async (bank) => {
    try {
      setLoading(true);
      const { data: bankData } = await axios.get('/bank-connections/line_bank');
      const account = bankData.bankaccount;
      const password = bankData.bankpassword;
      const id = bankData.bankid;
      const provider = "LINE_BANK";

      const res = await axios.post('/bank-connections/update_cash', { account, password, id, provider}, { headers: { "Content-Type": "application/json" } });
      setMainAccount(res.data.account_name);
      setAvailableBalance(res.data.available_balance);

      const nowIso = new Date().toISOString();
      setLastUpdated(nowIso);

      // 只更新被點擊的那一筆
      setBanks((prev) =>
        prev.map((x) =>
          x.bankid === id && String(x.provider).toUpperCase() === provider
            ? { ...x, account, cash: res.data.available_balance, last_update: nowIso }
            : x
        )
      );

    } catch (err) {
      const errMsg =
        err?.response?.data?.detail
          ? JSON.stringify(err.response.data.detail)
          : err?.response?.data?.error || err.message;
      alert(`Failed to update cash: ${errMsg}`);
    } finally {
      setLoading(false);
    }
  };

  const UpdateEsunbank = async (bank) => {
    try {
      setLoading(true);
      const { data: bankData } = await axios.get('/bank-connections/esun_bank');
      const account = bankData.bankaccount;
      const password = bankData.bankpassword;
      const id = bankData.bankid;
      const provider = "ESUN_BANK";

      const res = await axios.post('/bank-connections/update_cash', { account, password, id, provider}, { headers: { "Content-Type": "application/json" } });
      setMainAccount(res.data.account_name);
      setAvailableBalance(res.data.available_balance);

      const nowIso = new Date().toISOString();
      setLastUpdated(nowIso);

      // 只更新被點擊的那一筆
      setBanks((prev) =>
        prev.map((x) =>
          x.bankid === id && String(x.provider).toUpperCase() === provider
            ? { ...x, account, cash: res.data.available_balance, last_update: nowIso }
            : x
        )
      );

    } catch (err) {
      const errMsg =
        err?.response?.data?.detail
          ? JSON.stringify(err.response.data.detail)
          : err?.response?.data?.error || err.message;
      alert(`Failed to update cash: ${errMsg}`);
    } finally {
      setLoading(false);
    }
  };

  const UpdateCathaybank = async (bank) => {
    // TODO: CATHAY 的更新流程
    setBanner("Cathay Bank is not finished yet");
    setTimeout(() => setBanner(null), 2000);
  };

//###################################################################################################

  const providerUpdaters = {
    LINE_BANK: UpdateLinebank,
    ESUN_BANK: UpdateEsunbank,
    CATHAY_BANK: UpdateCathaybank,
  };

  // === 依 provider 呼叫對應的更新函式 ===
  const UpdateBankCash = async (bank, e) => {
    e?.stopPropagation?.(); // 避免觸發卡片 onClick
    const key = String(bank?.provider || "").toUpperCase();
    const fn = providerUpdaters[key];

    if (!fn) {
      setBanner(`暫不支援 ${key} 更新`);
      setTimeout(() => setBanner(null), 2000);
      return;
    }

    try {
      await fn(bank); // 有些函式需要 bank 物件，就把 bank 傳進去
    } catch (err) {
      console.error("Update error:", err);
      setBanner("更新失敗");
      setTimeout(() => setBanner(null), 2000);
    }
  };

  return (
    <div className={styles.screen} data-theme={theme}>
      <div className={styles.frame}>

        {/*left/ */}
        <div className={styles.left}>
          <div className={styles.sidebarGroupTitle}>General</div>
          <button onClick={() => navigate("/page1")} className={styles.navBtn}>
            🏠 Dashboard
          </button>
          <button onClick={() => navigate("/page2")} className={styles.navBtn}>
            📄 Reports
          </button>

          <div className={styles.sidebarGroupTitle}>Banks</div>
          <button onClick={() => navigate("/page3")} className={styles.navBtn}>
            💳 Connections
          </button>
          <button onClick={() => setShowAddContainer(true)} className={styles.navBtn}>
            ➕ Add Connection
          </button>

          <div className={styles.sidebarGroupTitle}>System</div>
            {/* Theme switch */}
            <label className={styles.themeSwitch}>
              <input
                type="checkbox"
                checked={theme === "light"}
                onChange={(e) => setTheme(e.target.checked ? "light" : "dark")}
                aria-label="Toggle light mode"
              />
              <span className={styles.slider}>
                <span className={styles.optionLeft}>🌙</span>
                <span className={styles.optionRight}>☀️</span>
                <span className={styles.knob} />
              </span>
              <span className={styles.switchText}>{theme === "light" ? "Light" : "Dark"}</span>
            </label>
            <button onClick={handleLogout} className={styles.navBtn}>
              ⏏ Logout
            </button>
        </div>

        <div className={styles.center}>
          <header className={styles.userBar}>
            <div className={styles.userLabel}>
              <span className={styles.userAvatar} />
              Welcome !!! {userAccount} {userEmail && `${userEmail}`}
            </div>
            {/*之後要用來一次更新全部bankCard     把更新function全部綁在這個按鈕 */}
            <button className={styles.userbutton} /*onClick={UpdateLinebank}*/ disabled={loading}>
              Update All Bank
            </button>
          </header>
          {banner && <div className={styles.toast}>{banner}</div>}

          {/*center/ */}
          <main className={styles.centerPanel}>
            <section className={styles.bankGrid}>
              {loading && (
                <div className={styles.loadingOverlay}>
                  <div className={styles.spinner}></div>
                  <p>Connecting...</p>
                </div>
              )}

              {banks.length === 0 ? (
                <div className={styles.emptyTip}>You don&apos;t have any connection</div>
              ) : (
                banks.map((b, idx) => (
                  <div
                    key={b.id ?? `${b.provider}-${idx}`}
                    className={styles.bankCard}
                  >
                    <div className={styles.bankHeader}>
                      <div className={styles.bankLogo}>
                        {getBankLogoSrc(b.provider) ? (
                          <img
                            className={styles.bankLogoImg}
                            src={getBankLogoSrc(b.provider)}
                            alt={`${(b.provider || "").replaceAll("_", " ")} logo`}
                            loading="lazy"
                            decoding="async"
                          />
                        ) : (
                          <span className={styles.bankLogoFallback}>{getProviderInitial(b.provider)}</span>
                        )}
                      </div>
                      <div>
                        <div className={styles.bankName}>{labelOf(b.provider)}</div>
                        <div className={styles.bankMeta}>{b.account_name || ""}</div>
                      </div>
                    </div>
                    <div className={styles.statRow}>
                      <span className={styles.chip}>
                        Balance: {b.cash ? formatCurrencyTWD(b.cash) : "—"}
                      </span>
                      <span className={styles.chip}>
                        Updated: {b.last_update ? formatTimeLocalTPE(b.last_update) : "—"}
                      </span>

                      <button
                        className={styles.deleteBtn}
                        onClick={(e) => UpdateBankCash(b, e)}
                      >
                        <img
                          src="/logo/updateButton.png"  // 修改為你的圖片路徑
                          alt="Delete"
                          className={styles.deleteIcon}
                        />
                      </button>

                      {/* Add Delete button */}
                      <button
                        className={styles.deleteBtn}
                        onClick={(e) => {
                          e.stopPropagation(); // 防止觸發卡片的點擊事件
                          handleOpenModal(b);     
                        }}
                      >
                        <img
                          src="/logo/deleteButton.png"  // 修改為你的圖片路徑
                          alt="Delete"
                          className={styles.deleteIcon}
                        />
                      </button>

                    </div>
                  </div>

                ))
              )}
            </section>
          </main>
            <ConfirmDeleteModal
              isOpen={isModalOpen}
              onCancel={handleCancelDelete}
              onConfirm={handleConfirmDelete}
              bank={selectedBank}
            />
            <button type="button" className={styles.fab} aria-label="Add Bank Connection" onClick={toggleAddContainer}>
              +
            </button>

          {showAddContainer && (
            <div className={styles.modal} onClick={toggleAddContainer}>
              <div className={styles.modalBody} onClick={(e) => e.stopPropagation()}>
                <h2 className={styles.modalTitle}>Bank Connection</h2>
                <form className={styles.form} onSubmit={handleSubmit}>
                  <select name="provider" value={form.provider} onChange={handleChange} required>
                    <option value="" disabled>
                      Select Bank
                    </option>
                    <option value="CATHAY_BANK">CATHAY_BANK</option>
                    <option value="ESUN_BANK">ESUN_BANK</option>
                    <option value="LINE_BANK">LINE_BANK</option>
                  </select>
                  <input
                    type="text"
                    name="bank_id"
                    value={form.bank_id}
                    onChange={handleChange}
                    placeholder="ID"
                    required
                  />
                  <input
                    type="text"
                    name="account"
                    value={form.account}
                    onChange={handleChange}
                    placeholder="Account"
                  />
                  <input
                    type="password"
                    name="password"
                    value={form.password}
                    onChange={handleChange}
                    placeholder="Password"
                  />
                  <div className={styles.formActions}>
                    <button type="submit" className={styles.primary}>
                      Connect
                    </button>
                  </div>
                </form>
                {message && <p className={styles.msg}>{message}</p>}
              </div>
            </div>
          )}
 
        </div>

        {/*right/ Version*/}
        <div className={styles.right}>
          <div style={{ padding: 16, lineHeight: 1.6, fontSize: 14 }}>
            <div style={{ marginBottom: 8 }}>Version：{versionNumber}</div>
            <div style={{ margin: "8px 0 6px", fontWeight: 600 }}>Support Bank</div>

            <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
              {Object.keys(PROVIDER_LABELS).map((key) => (
                <li
                  key={key}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 8,
                    padding: "6px 0",
                    borderBottom: "1px solid var(--border)",
                  }}
                >
                  {getBankLogoSrc(key) ? (
                    <img
                      src={getBankLogoSrc(key)}
                      alt={`${labelOf(key)} logo`}
                      width={20}
                      height={20}
                      style={{ objectFit: "contain" }}
                      loading="lazy"
                      decoding="async"
                    />
                  ) : (
                    <span
                      style={{
                        width: 20,
                        height: 20,
                        display: "grid",
                        placeItems: "center",
                        background: "var(--panel-2)",
                        borderRadius: 4,
                        fontSize: 12,
                        fontWeight: 700,
                      }}
                    >
                      {getProviderInitial(key)}
                    </span>
                  )}

                  <span>{labelOf(key)}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

      </div>
    </div>
  );
};

export default Dashboard;