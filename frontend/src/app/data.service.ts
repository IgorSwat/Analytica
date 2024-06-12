import { HttpClient, HttpParams, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { DataNormalization, DataVisualization, PcaInfo, ClusterInfo } from './models/data.model';
import { FeatureLabel } from './models/feature-types';

@Injectable({
  providedIn: 'root'
})
export class DataService {
  private getDataUrl = 'http://localhost:5000/data/visualize';
  private updateDataUrl = 'http://localhost:5000/data/update';
  private normalizeDataUrl = 'http://localhost:5000/data/normalize';
  private downloadDataUrl = 'http://localhost:5000/data/download';
  private getPcaInfoUrl = 'http://localhost:5000/data/pca/stats';
  private getPcaPlotUrl = 'http://localhost:5000/data/pca/plot';
  private updateFeatureSelectionUrl = 'http://localhost:5000/data/select-features';

  private getClusterInfoUrl = 'http://localhost:5000/data/cluster/compute';
  private getClusterPlotUrl = 'http://localhost:5000/data/cluster/plot';

  // A customizable field, will be replaced by user input in near future
  maxNoRecords: number = 100;

  constructor(private http: HttpClient) { }
  
  getData(recordsSelection: string = ""): Observable<DataVisualization> {
    if (recordsSelection == "")
      recordsSelection = "1-" + this.maxNoRecords.toString();

    const params = new HttpParams().set('selection', recordsSelection);
    return this.http.get<DataVisualization>(this.getDataUrl, {params});
  }

  updateData(featureLabels: FeatureLabel[], featureStates: boolean[]): Observable<any> {  
    const paramArray : number[] = Array.from({length: featureLabels.length}, (_, index) => {
      return <number>featureLabels[index].featureType;
    })
    const body = JSON.stringify({"types": paramArray, "states": featureStates});
    const headers = new HttpHeaders({ 'Content-Type': 'application/json' });

    return this.http.put(this.updateDataUrl, body, {headers});
  }

  downloadData(): Observable<any> {
    return this.http.get(this.downloadDataUrl, {responseType: 'blob'});
  }

  getNormalizedData(numericMethod: string = 'standard'): Observable<DataNormalization> {
    const params = new HttpParams().set('numeric_method', numericMethod);
    return this.http.get<DataNormalization>(this.normalizeDataUrl, {params});
  }

  getPcaInfo() : Observable<PcaInfo> {
    return this.http.get<PcaInfo>(this.getPcaInfoUrl, {});
  }

  getPcaPlot(plotID: number) : Observable<any> {
    const params = new HttpParams().set('plot_id', plotID.toString());
    return this.http.get<any>(this.getPcaPlotUrl, {params});
  }

  getClusterInfo() : Observable<ClusterInfo> {
    return this.http.get<ClusterInfo>(this.getClusterInfoUrl, {});
  }

  getClusterPlot(plotID: number) : Observable<any> {
    const params = new HttpParams().set('plot_id', plotID.toString());
    return this.http.get<any>(this.getClusterPlotUrl, {params});
  }

  updateFeatureSelection(featureStates: boolean[]): Observable<any> {
    const body = JSON.stringify(featureStates);
    const headers = new HttpHeaders({ 'Content-Type': 'application/json' });

    return this.http.put(this.updateFeatureSelectionUrl, body, {headers});
  }
  
}
