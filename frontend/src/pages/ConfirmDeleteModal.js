// ConfirmDeleteModal.js
import React from 'react';
import styles from './Dashboard.module.css';

const ConfirmDeleteModal = ({ isOpen, onCancel, onConfirm, bank }) => {
  if (!isOpen) return null;

  return (
    <div className={styles.modal} onClick={onCancel}>
      <div className={styles.modalBody} onClick={(e) => e.stopPropagation()}>
        <h2 className={styles.modalTitle}>Delete Bank Connection</h2>
        <p className={styles.msg}>
          {bank?.provider?.replaceAll('_',' ')}
          {bank?.bankid ? `（ID: ${bank.bankid}）` : ''}will be deleted forever
        </p>
        <div className={styles.formActions}>
          <button type="button" className={styles.primary} onClick={onConfirm}>
            Delete
          </button>
          <button type="button" className={styles.navBtn} onClick={onCancel}>
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmDeleteModal;
