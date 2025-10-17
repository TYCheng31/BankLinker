import React, { useState, useEffect } from "react";
import axios from "axios";
import { Routes, Route, useNavigate, Outlet} from "react-router-dom";
import styles from "./Dashboard.module.css";
import ConfirmDeleteModal from './ConfirmDeleteModal';
import {normalizeConnections, maskAccount, getProviderInitial, formatTime, formatCurrencyTWD, formatTimeLocalTPE, BANK_LOGOS, getBankLogoSrc, PROVIDER_LABELS, labelOf} from '../utils/utils';

const versionNumber = "v1.4.1 250923";
   
const Dashboard = () => {
  const navigate = useNavigate();

  const [form, setForm] = useState({ bank_id: "", provider: "", account: "", password: ""});
  const [message, setMessage] = useState("");
  const [banks, setBanks] = useState([]);
  const [showAddContainer, setShowAddContainer] = useState(false);
  const [loading, setLoading] = useState(false);
  const [userAccount, setUserAccount] = useState("");
  const [userEmail, setUserEmail] = useState("");
  const [theme, setTheme] = useState("dark");      
  const [banner, setBanner] = useState(null);
  const [selectedBank, setSelectedBank] = useState(null); 
  const [isModalOpen, setIsModalOpen] = useState(false); 
  const [totalAssets, setTotalAssets] = useState(0);
  const [totalCash, setTotalCash] = useState(0); // 用來儲存總現金
  const [totalStock, setTotalStock] = useState(0); // 用來儲存總股票
  const [visibleStep, setVisibleStep] = useState(0);

  const calculateTotalAssets = () => {
    let total = 0;  // 總財產
    let cash = 0;   // 總現金
    let stock = 0;  // 總股票

    // 遍歷所有的銀行帳戶，累加現金和股票
    banks.forEach((bank) => {
      const bankCash = bank.BcCash || 0;  // 如果沒有 BcCash，就視為 0
      const bankStock = bank.BcStock || 0; // 如果沒有 BcStock，就視為 0

      total += bankCash + bankStock;  // 累加現金和股票，得到總財產
      cash += bankCash;  // 累加現金
      stock += bankStock; // 累加股票
    });

    setTotalAssets(total);  // 更新總財產
    setTotalCash(cash);     // 更新總現金
    setTotalStock(stock);   // 更新總股票
  };

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
        console.log("aaaa",response.data);
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

  useEffect(() => {
    // 每次 banks 更新時計算總財產
    calculateTotalAssets();
  }, [banks]);  // 依賴於 banks，當 banks 更新時重新計算


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
          account_name: res.data.account_name,
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
      const mainAccount = res.data.account_name
      const nowIso = new Date().toISOString();

      // 只更新被點擊的那一筆
      setBanks((prev) =>
        prev.map((x) =>
          x.bankid === id && String(x.provider).toUpperCase() === provider
            ? { ...x, account, cash: res.data.available_balance, last_update: nowIso, mainAccount }
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
      const mainAccount = res.data.account_name
      const stock = res.data.stock
      console.log(stock)
      const nowIso = new Date().toISOString();

      // 只更新被點擊的那一筆
      setBanks((prev) =>
        prev.map((x) =>
          x.bankid === id && String(x.provider).toUpperCase() === provider
            ? { ...x, account, cash: res.data.available_balance, last_update: nowIso, mainAccount, stock }
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
    try {
      setLoading(true);
      const { data: bankData } = await axios.get('/bank-connections/cathay_bank');
      const account = bankData.bankaccount;
      const password = bankData.bankpassword;
      const id = bankData.bankid;
      const provider = "CATHAY_BANK";

      const res = await axios.post('/bank-connections/update_cash', { account, password, id, provider}, { headers: { "Content-Type": "application/json" } });
      const mainAccount = res.data.account_name
      const stock = res.data.stock
      console.log(stock)
      const nowIso = new Date().toISOString();

      // 只更新被點擊的那一筆
      setBanks((prev) =>
        prev.map((x) =>
          x.bankid === id && String(x.provider).toUpperCase() === provider
            ? { ...x, account, cash: res.data.available_balance, last_update: nowIso, mainAccount, stock }
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
      window.location.reload();
    } catch (err) {
      console.error("Update error:", err);
      setBanner("更新失敗");
      setTimeout(() => setBanner(null), 2000);
    }
    //刷新頁面

  };

  useEffect(() => {
    if (loading) {
      const timeout1 = setTimeout(() => setVisibleStep(1), 500);  // 顯示第一個文字
      const timeout2 = setTimeout(() => setVisibleStep(2), 2500); // 顯示第二個文字
      const timeout3 = setTimeout(() => setVisibleStep(3), 5500); // 顯示第三個文字

      // 清除定時器
      return () => {
        clearTimeout(timeout1);
        clearTimeout(timeout2);
        clearTimeout(timeout3);
      };
    }
  }, [loading]);

  return (
    <div className={styles.screen} data-theme={theme}>
      <div className={styles.frame}>

        {/*left/ */}
        <div className={styles.left}>
          <div className={styles.sidebarGroupTitle}>General</div>

          <button onClick={() => navigate("")} className={styles.navBtn}>
            <img
              src="/logo/homeButton.png"  // 修改為你的圖片路徑
              alt="Delete"
              className={styles.deleteIcon}
            />
            HOME
          </button>

          <button onClick={() => navigate("home")} className={styles.navBtn}>
            <img
              src="/logo/linkerButton.png"  // 修改為你的圖片路徑
              alt="Delete"
              className={styles.deleteIcon}
            />
            LINKER
          </button>

          <button onClick={() => navigate("reports")} className={styles.navBtn}>
            <img
              src="/logo/settingButton.png"  // 修改為你的圖片路徑
              alt="Delete"
              className={styles.deleteIcon}
            />
            ANALYSIS
          </button>

          <div className={styles.sidebarGroupTitle}>Banks</div>
          <button onClick={() => setShowAddContainer(true)} className={styles.navBtn}>
            <img
              src="/logo/addButton.png"  // 修改為你的圖片路徑
              alt="Delete"
              className={styles.deleteIcon}
            />
            ADD BANK
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
              <img
                src="/logo/logoutButton.png"  // 修改為你的圖片路徑
                alt="Delete"
                className={styles.deleteIcon}
              />
              LOGOUT
            </button>
        </div>

        <div className={styles.center}>

          <main className={styles.centerPanel}>
            <Routes>
              <Route path="" element={
                <div>

                  <div>
                    You can click the Linker Button to connect your bank account.
                  </div>

                  <div>
                    Click the setting button to setup the update time.
                  </div>

                </div>
              }/>

              <Route path="/home" element={
                <div>
                  <header className={styles.userBar}>
                    <div className={styles.userLabel}>
                      <span className={styles.userAvatar} />
                      <div className={styles.userInfo}>
                        <div className={styles.welcomeText}>
                          Welcome !!! {userAccount} {userEmail && `${userEmail}`}
                        </div>
                        <div className={styles.totalAssets}>
                          <strong>Total Assets: </strong>
                          NT$ {formatCurrencyTWD(totalAssets)}
                        </div>
                      </div>
                    </div>
                    <div>
                      <p>CASH: NT$ {formatCurrencyTWD(totalCash)}</p>
                      <p>STOCK: NT$ {formatCurrencyTWD(totalStock)}</p>
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
                          {visibleStep >= 1 && <p>Linking Your Bank Account! Please Wait!</p>}
                          {visibleStep >= 2 && <p>Fetching Your Balance ...</p>}
                          {visibleStep >= 3 && <p>It's almost done!</p>}
                        </div>
                      )}

                      {banks.length === 0 ? (<div className={styles.emptyTip}>You don&apos;t have any connection</div>) : (banks.map((b, idx) => (
                          <div key={b.id ?? `${b.provider}-${idx}`} className={styles.bankCard}>
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
                                <div className={styles.bankMeta}>{b.BcMainaccount}</div>
                              </div>

                            </div>

                            <div className={styles.chip}>
                              Cash NT$ {b.BcCash ? formatCurrencyTWD(b.BcCash) : " ---"}
                            </div>   

                            <div className={styles.chip}>    
                              Stock NT$ {b.BcStock !== null && b.BcStock !== undefined ? formatCurrencyTWD(b.BcStock) : "---"}
                            </div> 

                            <div className={styles.chiptime}>
                              Last Update {b.last_update ? formatTimeLocalTPE(b.last_update) : "NO DATA"}
                            </div>

                            <div className={styles.statRow}>

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
                      <img
                        src="/logo/addbankButton.png"  // 修改為你的圖片路徑
                        alt="Delete"
                        className={styles.deleteIcon}
                      />
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
                            <option value="CH_BANK">CH_BANK</option>
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
                </div>}/>
              <Route path="/reports" element={
                <div>
                  <button >發送 Email</button>
                </div>
              } />
            </Routes>
          </main>


 
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