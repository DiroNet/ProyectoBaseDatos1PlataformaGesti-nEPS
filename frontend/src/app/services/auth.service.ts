import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'http://localhost:5000/api';
  private tokenKey = 'auth_token';
  private userKey = 'user_data';

  currentUser = signal<any>(this.getStoredUser());

  constructor(private http: HttpClient) {}

  login(email: string, password: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/auth/login`, { email, password }).pipe(
      tap((response: any) => {
        localStorage.setItem(this.tokenKey, response.token);
        localStorage.setItem(this.userKey, JSON.stringify(response.usuario));
        this.currentUser.set(response.usuario);
      })
    );
  }

  register(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/auth/register`, data);
  }

  logout(): void {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.userKey);
    this.currentUser.set(null);
  }

  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  isLoggedIn(): boolean {
    return !!this.getToken();
  }

  getUser(): any {
    return this.currentUser();
  }

  getUserRole(): string {
    const user = this.getUser();
    return user?.rol_nombre || '';
  }

  private getStoredUser(): any {
    const stored = localStorage.getItem(this.userKey);
    return stored ? JSON.parse(stored) : null;
  }
}