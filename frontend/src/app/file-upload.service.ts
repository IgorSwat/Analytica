import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { DataService } from './data.service';

@Injectable({
  providedIn: 'root'
})

export class FileUploadService {
  private uploadUrl = "http://localhost:5000/upload";

  constructor(private http : HttpClient, private dataService: DataService) { }

  uploadFile(file: File): Observable<any> {
    const formData: FormData = new FormData();
    formData.append('file', file, file.name);
    this.dataService.getData();
    return this.http.post(this.uploadUrl, formData);


  }
  
}
