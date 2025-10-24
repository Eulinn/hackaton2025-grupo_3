import { toast, type TypeOptions, type ToastOptions } from 'react-toastify';

const toastOptions: ToastOptions  = {
  position: "top-right",
  autoClose: 5000,
  hideProgressBar: false,
  closeOnClick: true,
  pauseOnHover: true,
  draggable: true,
  progress: undefined,
};


const showToast = (message: string, type: TypeOptions) => {
  toast(message, {
    ...toastOptions,
    type: type,
  });
};

// --- FUNÇÕES EXPORTÁVEIS ---

export const showSuccessToast = (message: string) => {
  showToast(message, 'success');
};

export const showErrorToast = (message: string) => {
  showToast(message, 'error');
};

export const showInfoToast = (message: string) => {
  showToast(message, 'info');
};

export const showWarningToast = (message: string) => {
  showToast(message, 'warning');
};