import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { DataVisualization } from './models/data.model';

@Injectable({
  providedIn: 'root'
})
export class DataService {
  private apiUrl = 'http://localhost:5000/data/visualize';

  // A customizable field, will be replaced by user input in near future
  maxNoRecords: number = 100;

  constructor(private http: HttpClient) { }
  
  getData(recordsSelection: string = ""): Observable<DataVisualization> {
    if (recordsSelection == "")
      recordsSelection = "1-" + this.maxNoRecords.toString();

    const params = new HttpParams().set('selection', recordsSelection);
    return this.http.get<DataVisualization>(this.apiUrl, {params});
  }
  
}
