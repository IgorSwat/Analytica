import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})

export class AppStateService {
  private apiUrl = "http://localhost:5000/navbar";

  // False means disabled
  // You can unlock to test some buttons
  private navButtonsState = new BehaviorSubject<{ [key: string]: boolean}>({
    "nav-data": false,
    "nav-normalize": false,
    "nav-pca": false,
    "nav-clusters": false
  });
  public navButtonsState$ = this.navButtonsState.asObservable();

  constructor(private http: HttpClient) { }

  updateNavbarState(): void {
    this.http.get<any>(this.apiUrl, {}).subscribe({
      next: (states) => {
        this.navButtonsState.next({
          "nav-data": states["nav-data"],
          "nav-normalize": states["nav-normalize"],
          "nav-pca": states["nav-pca"],
          "nav-clusters": states["nav-clusters"]
        });
      },
      error: (err) => console.error('Error fetching data:', err)
    });
  }
}
