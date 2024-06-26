import { HttpClient, HttpParams, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ClusterData, DataNormalization, DataVisualization, PcaData} from './models/data.model';
import { FeatureLabel } from './models/feature-types';

@Injectable({
  providedIn: 'root'
})
export class DataService {
  private getDataUrl = 'http://localhost:5000/data/visualize';
  private updateDataUrl = 'http://localhost:5000/data/update';
  private normalizeDataUrl = 'http://localhost:5000/data/normalize';
  private downloadDataUrl = 'http://localhost:5000/data/download';
  private getPcaDataUrl = 'http://localhost:5000/data/pca';
  private getPcaPlotUrl = 'http://localhost:5000/data/pca/plot';
  private updateFeatureSelectionUrl = 'http://localhost:5000/data/select-features';
  private clusterizeDataUrl = 'http://localhost:5000/data/clustering';
  private getClusterPlotUrl = 'http://localhost:5000/data/clustering/plot';
  private downloadClusterDataUrl = 'http://localhost:5000/data/clustering/download';

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

  getPcaData(noComponents: number) : Observable<PcaData> {
    const params = new HttpParams().set('n_components', noComponents);
    return this.http.get<PcaData>(this.getPcaDataUrl, {params});
  }

  getPcaPlot(plotID: number) : Observable<any> {
    const params = new HttpParams().set('plot_id', plotID.toString());
    return this.http.get<any>(this.getPcaPlotUrl, {params});
  }

  clusterizeData(clustering_method: string, n_clusters: number, eps: number, min_samples: number, linkage: string) : Observable<ClusterData> {
    const params = new HttpParams().appendAll({
      'clustering_method': clustering_method,
      'n_clusters': n_clusters,
      'eps': eps,
      'min_samples': min_samples,
      'linkage': linkage
    });
    return this.http.get<ClusterData>(this.clusterizeDataUrl, {params});
  }

  getClusterPlot() : Observable<any> {
    return this.http.get<any>(this.getClusterPlotUrl, {});
  }

  downloadClusterData(rawFlag: boolean = true) : Observable<any> {
    const params = new HttpParams().set('raw_flag', rawFlag.toString());
    return this.http.get(this.downloadClusterDataUrl, {responseType: 'blob', params: params});
  }

  updateFeatureSelection(featureStates: boolean[]): Observable<any> {
    const body = JSON.stringify(featureStates);
    const headers = new HttpHeaders({ 'Content-Type': 'application/json' });

    return this.http.put(this.updateFeatureSelectionUrl, body, {headers});
  }
  
}
