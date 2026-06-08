import { inject } from '@angular/core';
import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { Router } from '@angular/router';
import { NotificationService } from '../services/notification.service';
import { catchError, throwError } from 'rxjs';

export const ErrorInterceptor: HttpInterceptorFn = (req, next) => {
  const router = inject(Router);
  const notification = inject(NotificationService);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401) {
        notification.error('Sesión expirada. Por favor inicia sesión nuevamente.');
        router.navigate(['/login']);
      } else if (error.status === 403) {
        notification.error('No tienes permiso para realizar esta acción.');
      } else if (error.status === 404) {
        notification.error('El recurso solicitado no fue encontrado.');
      } else if (error.status >= 500) {
        notification.error('Error del servidor. Intenta más tarde.');
      } else if (error.status === 0) {
        notification.error('No se pudo conectar con el servidor.');
      } else if (error.error && error.error.error) {
        notification.error(error.error.error);
      }
      return throwError(() => error);
    })
  );
};