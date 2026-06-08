import { Injectable } from '@angular/core';
import Swal from 'sweetalert2';

@Injectable({
  providedIn: 'root'
})
export class NotificationService {

  success(message: string): void {
    Swal.fire({
      icon: 'success',
      title: 'Éxito',
      text: message,
      confirmButtonColor: '#0369a1',
      background: '#FFFFFF',
      color: '#1E293B',
      confirmButtonText: 'Aceptar'
    });
  }

  error(message: string): void {
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: message,
      confirmButtonColor: '#DC2626',
      background: '#FFFFFF',
      color: '#1E293B',
      confirmButtonText: 'Aceptar'
    });
  }

  warning(message: string): void {
    Swal.fire({
      icon: 'warning',
      title: 'Advertencia',
      text: message,
      confirmButtonColor: '#D97706',
      background: '#FFFFFF',
      color: '#1E293B',
      confirmButtonText: 'Aceptar'
    });
  }

  info(message: string): void {
    Swal.fire({
      icon: 'info',
      title: 'Información',
      text: message,
      confirmButtonColor: '#0369a1',
      background: '#FFFFFF',
      color: '#1E293B',
      confirmButtonText: 'Aceptar'
    });
  }

  confirm(message: string, callback: () => void): void {
    Swal.fire({
      icon: 'question',
      title: 'Confirmar',
      text: message,
      showCancelButton: true,
      confirmButtonColor: '#0369a1',
      cancelButtonColor: '#64748B',
      background: '#FFFFFF',
      color: '#1E293B',
      confirmButtonText: 'Sí, continuar',
      cancelButtonText: 'Cancelar'
    }).then((result) => {
      if (result.isConfirmed) {
        callback();
      }
    });
  }

  confirmDanger(message: string, callback: () => void): void {
    Swal.fire({
      icon: 'warning',
      title: '¿Está seguro?',
      text: message,
      showCancelButton: true,
      confirmButtonColor: '#DC2626',
      cancelButtonColor: '#64748B',
      background: '#FFFFFF',
      color: '#1E293B',
      confirmButtonText: 'Sí, eliminar',
      cancelButtonText: 'Cancelar'
    }).then((result) => {
      if (result.isConfirmed) {
        callback();
      }
    });
  }

  toast(message: string, type: 'success' | 'error' | 'warning' | 'info' = 'success'): void {
    const Toast = Swal.mixin({
      toast: true,
      position: 'top-end',
      showConfirmButton: false,
      timer: 3000,
      timerProgressBar: true,
      background: '#FFFFFF',
      color: '#1E293B',
      didOpen: (toast) => {
        toast.onmouseenter = Swal.stopTimer;
        toast.onmouseleave = Swal.resumeTimer;
      }
    });

    Toast.fire({
      icon: type,
      title: message
    });
  }
}
