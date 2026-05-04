import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = 'http://localhost:5000/api';

  constructor(private http: HttpClient, private authService: AuthService) {}

  private getHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });
  }

  // Citas
  getCitas(filters?: any): any {
    let url = `${this.apiUrl}/citas`;
    if (filters) {
      const params = new URLSearchParams();
      Object.keys(filters).forEach(key => {
        if (filters[key]) params.append(key, filters[key]);
      });
      url += '?' + params.toString();
    }
    return this.http.get(url, { headers: this.getHeaders() });
  }

  createCita(data: any): any {
    return this.http.post(`${this.apiUrl}/citas`, data, { headers: this.getHeaders() });
  }

  updateCita(id: number, data: any): any {
    return this.http.put(`${this.apiUrl}/citas/${id}`, data, { headers: this.getHeaders() });
  }

  deleteCita(id: number): any {
    return this.http.delete(`${this.apiUrl}/citas/${id}`, { headers: this.getHeaders() });
  }

  // Médicos
  getMedicos(): any {
    return this.http.get(`${this.apiUrl}/medicos`, { headers: this.getHeaders() });
  }

  createMedico(data: any): any {
    return this.http.post(`${this.apiUrl}/medicos`, data, { headers: this.getHeaders() });
  }

  updateMedico(id: number, data: any): any {
    return this.http.put(`${this.apiUrl}/medicos/${id}`, data, { headers: this.getHeaders() });
  }

  deleteMedico(id: number): any {
    return this.http.delete(`${this.apiUrl}/medicos/${id}`, { headers: this.getHeaders() });
  }

  // Especialidades
  getEspecialidades(): any {
    return this.http.get(`${this.apiUrl}/especialidades`, { headers: this.getHeaders() });
  }

  createEspecialidad(data: any): any {
    return this.http.post(`${this.apiUrl}/especialidades`, data, { headers: this.getHeaders() });
  }

  updateEspecialidad(id: number, data: any): any {
    return this.http.put(`${this.apiUrl}/especialidades/${id}`, data, { headers: this.getHeaders() });
  }

  deleteEspecialidad(id: number): any {
    return this.http.delete(`${this.apiUrl}/especialidades/${id}`, { headers: this.getHeaders() });
  }

  // Estados
  getEstados(): any {
    return this.http.get(`${this.apiUrl}/estados`, { headers: this.getHeaders() });
  }

  createEstado(data: any): any {
    return this.http.post(`${this.apiUrl}/estados`, data, { headers: this.getHeaders() });
  }

  getMedico(id: number): any {
    return this.http.get(`${this.apiUrl}/medicos/${id}`, { headers: this.getHeaders() });
  }

  getDisponibilidadMedico(id: number): any {
    return this.http.get(`${this.apiUrl}/disponibilidad/medico/${id}`, { headers: this.getHeaders() });
  }

  // Pacientes
  getPacientes(): any {
    return this.http.get(`${this.apiUrl}/pacientes`, { headers: this.getHeaders() });
  }

  getPaciente(id: number): any {
    return this.http.get(`${this.apiUrl}/pacientes/${id}`, { headers: this.getHeaders() });
  }

  // Historial
  getHistorialPaciente(pacienteId: number): any {
    return this.http.get(`${this.apiUrl}/historial/paciente/${pacienteId}`, { headers: this.getHeaders() });
  }

  createHistorial(data: any): any {
    return this.http.post(`${this.apiUrl}/historial`, data, { headers: this.getHeaders() });
  }

  // Disponibilidad
  createDisponibilidad(medicoId: number, data: any): any {
    return this.http.post(`${this.apiUrl}/disponibilidad/medico/${medicoId}`, data, { headers: this.getHeaders() });
  }

  updateDisponibilidad(id: number, data: any): any {
    return this.http.put(`${this.apiUrl}/disponibilidad/${id}`, data, { headers: this.getHeaders() });
  }

  // Usuarios
  getUsuarios(): any {
    return this.http.get(`${this.apiUrl}/usuarios`, { headers: this.getHeaders() });
  }

  updateUsuario(id: number, data: any): any {
    return this.http.put(`${this.apiUrl}/usuarios/${id}`, data, { headers: this.getHeaders() });
  }

  deleteUsuario(id: number): any {
    return this.http.delete(`${this.apiUrl}/usuarios/${id}`, { headers: this.getHeaders() });
  }
}