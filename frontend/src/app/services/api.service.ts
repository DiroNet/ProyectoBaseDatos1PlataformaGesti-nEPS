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
      'Authorization': 'Bearer ' + token
    });
  }

  initDB(): any {
    return this.http.post(this.apiUrl + '/init', {});
  }

  getUsuarios(): any {
    return this.http.get(this.apiUrl + '/usuarios', { headers: this.getHeaders() });
  }

  getUsuario(id: number): any {
    return this.http.get(this.apiUrl + '/usuarios/' + id, { headers: this.getHeaders() });
  }

  updateUsuario(id: number, data: any): any {
    return this.http.put(this.apiUrl + '/usuarios/' + id, data, { headers: this.getHeaders() });
  }

  deleteUsuario(id: number): any {
    return this.http.delete(this.apiUrl + '/usuarios/' + id, { headers: this.getHeaders() });
  }

  getAfiliados(): any {
    return this.http.get(this.apiUrl + '/afiliados', { headers: this.getHeaders() });
  }

  getAfiliado(id: number): any {
    return this.http.get(this.apiUrl + '/afiliados/' + id, { headers: this.getHeaders() });
  }

  createAfiliado(data: any): any {
    return this.http.post(this.apiUrl + '/afiliados', data, { headers: this.getHeaders() });
  }

  updateAfiliado(id: number, data: any): any {
    return this.http.put(this.apiUrl + '/afiliados/' + id, data, { headers: this.getHeaders() });
  }

  deleteAfiliado(id: number): any {
    return this.http.delete(this.apiUrl + '/afiliados/' + id, { headers: this.getHeaders() });
  }

  getProfesionales(): any {
    return this.http.get(this.apiUrl + '/profesionales', { headers: this.getHeaders() });
  }

  getProfesional(id: number): any {
    return this.http.get(this.apiUrl + '/profesionales/' + id, { headers: this.getHeaders() });
  }

  createProfesional(data: any): any {
    return this.http.post(this.apiUrl + '/profesionales', data, { headers: this.getHeaders() });
  }

  updateProfesional(id: number, data: any): any {
    return this.http.put(this.apiUrl + '/profesionales/' + id, data, { headers: this.getHeaders() });
  }

  deleteProfesional(id: number): any {
    return this.http.delete(this.apiUrl + '/profesionales/' + id, { headers: this.getHeaders() });
  }

  getCentros(): any {
    return this.http.get(this.apiUrl + '/centros', { headers: this.getHeaders() });
  }

  getCentro(id: number): any {
    return this.http.get(this.apiUrl + '/centros/' + id, { headers: this.getHeaders() });
  }

  createCentro(data: any): any {
    return this.http.post(this.apiUrl + '/centros', data, { headers: this.getHeaders() });
  }

  updateCentro(id: number, data: any): any {
    return this.http.put(this.apiUrl + '/centros/' + id, data, { headers: this.getHeaders() });
  }

  deleteCentro(id: number): any {
    return this.http.delete(this.apiUrl + '/centros/' + id, { headers: this.getHeaders() });
  }

  getPlanes(): any {
    return this.http.get(this.apiUrl + '/planes', { headers: this.getHeaders() });
  }

  getPlan(id: number): any {
    return this.http.get(this.apiUrl + '/planes/' + id, { headers: this.getHeaders() });
  }

  createPlan(data: any): any {
    return this.http.post(this.apiUrl + '/planes', data, { headers: this.getHeaders() });
  }

  updatePlan(id: number, data: any): any {
    return this.http.put(this.apiUrl + '/planes/' + id, data, { headers: this.getHeaders() });
  }

  deletePlan(id: number): any {
    return this.http.delete(this.apiUrl + '/planes/' + id, { headers: this.getHeaders() });
  }

  getDisponibilidad(profesionalId: number): any {
    return this.http.get(this.apiUrl + '/disponibilidad/' + profesionalId, { headers: this.getHeaders() });
  }

  createDisponibilidad(data: any): any {
    return this.http.post(this.apiUrl + '/disponibilidad', data, { headers: this.getHeaders() });
  }

  deleteDisponibilidad(id: number): any {
    return this.http.delete(this.apiUrl + '/disponibilidad/' + id, { headers: this.getHeaders() });
  }

  getCitas(filters?: any): any {
    let url = this.apiUrl + '/citas';
    if (filters) {
      const params = new URLSearchParams();
      Object.keys(filters).forEach(key => {
        if (filters[key]) params.append(key, filters[key]);
      });
      url += '?' + params.toString();
    }
    return this.http.get(url, { headers: this.getHeaders() });
  }

  getCita(id: number): any {
    return this.http.get(this.apiUrl + '/citas/' + id, { headers: this.getHeaders() });
  }

  createCita(data: any): any {
    return this.http.post(this.apiUrl + '/citas', data, { headers: this.getHeaders() });
  }

  updateCita(id: number, data: any): any {
    return this.http.put(this.apiUrl + '/citas/' + id, data, { headers: this.getHeaders() });
  }

  deleteCita(id: number): any {
    return this.http.delete(this.apiUrl + '/citas/' + id, { headers: this.getHeaders() });
  }

  getFacturas(filters?: any): any {
    let url = this.apiUrl + '/facturas';
    if (filters) {
      const params = new URLSearchParams();
      Object.keys(filters).forEach(key => {
        if (filters[key]) params.append(key, filters[key]);
      });
      url += '?' + params.toString();
    }
    return this.http.get(url, { headers: this.getHeaders() });
  }

  getFactura(id: number): any {
    return this.http.get(this.apiUrl + '/facturas/' + id, { headers: this.getHeaders() });
  }

  createFactura(data: any): any {
    return this.http.post(this.apiUrl + '/facturas', data, { headers: this.getHeaders() });
  }

  pagarFactura(id: number, metodoPago: string): any {
    return this.http.post(this.apiUrl + '/facturas/' + id + '/pagar', { metodo_pago: metodoPago }, { headers: this.getHeaders() });
  }

  updateFactura(id: number, data: any): any {
    return this.http.put(this.apiUrl + '/facturas/' + id, data, { headers: this.getHeaders() });
  }

  deleteFactura(id: number): any {
    return this.http.delete(this.apiUrl + '/facturas/' + id, { headers: this.getHeaders() });
  }

  getPagos(): any {
    return this.http.get(this.apiUrl + '/pagos', { headers: this.getHeaders() });
  }

  getHistorial(): any {
    return this.http.get(this.apiUrl + '/historial', { headers: this.getHeaders() });
  }

  createHistorial(data: any): any {
    return this.http.post(this.apiUrl + '/historial', data, { headers: this.getHeaders() });
  }

  updateHistorial(id: number, data: any): any {
    return this.http.put(this.apiUrl + '/historial/' + id, data, { headers: this.getHeaders() });
  }

  getCitasProximas(): any {
    return this.http.get(this.apiUrl + '/consultas/citas-proximas-afiliado', { headers: this.getHeaders() });
  }

  getAfiliadosFacturasPendientes(): any {
    return this.http.get(this.apiUrl + '/consultas/afiliados-facturas-pendientes', { headers: this.getHeaders() });
  }

  getFacturacionPorPlan(): any {
    return this.http.get(this.apiUrl + '/consultas/facturacion-por-plan', { headers: this.getHeaders() });
  }

  getDiagnosticosFrecuentes(): any {
    return this.http.get(this.apiUrl + '/consultas/diagnosticos-frecuentes', { headers: this.getHeaders() });
  }

  getCentrosMasUtilizados(): any {
    return this.http.get(this.apiUrl + '/consultas/centros-mas-utilizados', { headers: this.getHeaders() });
  }

  getDashboardEstadisticas(): any {
    return this.http.get(this.apiUrl + '/dashboard/estadisticas', { headers: this.getHeaders() });
  }
}
