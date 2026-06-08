import { Injectable } from '@angular/core';
import { BehaviorSubject, interval } from 'rxjs';
import { ApiService } from './api.service';

@Injectable({
  providedIn: 'root'
})
export class RealtimeService {
  private refreshInterval = 5000;
  private intervals: Map<string, any> = new Map();

  private dataChanged$ = new BehaviorSubject<{ type: string; data?: any } | null>(null);

  constructor(private api: ApiService) {}

  onDataChange() {
    return this.dataChanged$.asObservable();
  }

  notifyChange(type: string, data?: any): void {
    this.dataChanged$.next({ type, data });
  }

  startPolling(key: string, callback: () => void): void {
    this.stopPolling(key);
    const subscription = interval(this.refreshInterval).subscribe(() => {
      callback();
    });
    this.intervals.set(key, subscription);
  }

  stopPolling(key: string): void {
    if (this.intervals.has(key)) {
      this.intervals.get(key).unsubscribe();
      this.intervals.delete(key);
    }
  }

  stopAllPolling(): void {
    this.intervals.forEach(sub => sub.unsubscribe());
    this.intervals.clear();
  }

  setInterval(ms: number): void {
    this.refreshInterval = ms;
  }
}