import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class DataRefreshService {
  private refreshTrigger = new BehaviorSubject<string>('');
  refresh$ = this.refreshTrigger.asObservable();

  triggerRefresh(component: string): void {
    this.refreshTrigger.next(component);
  }

  triggerAllRefresh(): void {
    this.refreshTrigger.next('all');
  }
}