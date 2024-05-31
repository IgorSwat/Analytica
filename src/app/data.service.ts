import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { DataVisualization } from './models/data.model';

@Injectable({
  providedIn: 'root'
})
export class DataService {
  private apiUrl = 'http://localhost:5000/data/visualize';

  constructor(private http: HttpClient) { }
  getData(): Observable<DataVisualization> {
    return this.http.get<DataVisualization>(this.apiUrl);
  }
  
}
