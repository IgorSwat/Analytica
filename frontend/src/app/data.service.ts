import { HttpClient, HttpParams, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { DataVisualization } from './models/data.model';
import { FeatureLabel } from './models/feature-types';

@Injectable({
  providedIn: 'root'
})
export class DataService {
  private getDataUrl = 'http://localhost:5000/data/visualize';
  private updateDataUrl = 'http://localhost:5000/data/update';

  // A customizable field, will be replaced by user input in near future
  maxNoRecords: number = 100;

  constructor(private http: HttpClient) { }
  
  getData(recordsSelection: string = ""): Observable<DataVisualization> {
    if (recordsSelection == "")
      recordsSelection = "1-" + this.maxNoRecords.toString();

    const params = new HttpParams().set('selection', recordsSelection);
    return this.http.get<DataVisualization>(this.getDataUrl, {params});
  }

  updateData(featureLabels: FeatureLabel[]): Observable<any> {  
    const paramArray : number[] = Array.from({length: featureLabels.length}, (_, index) => {
      return <number>featureLabels[index].featureType;
    })
    const body = JSON.stringify(paramArray);
    const headers = new HttpHeaders({ 'Content-Type': 'application/json' });

    return this.http.put(this.updateDataUrl, body, {headers});
  }
  
}
