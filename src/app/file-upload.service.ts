import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})

export class FileUploadService {
  private uploadUrl = "https://localhost:3000/upload";

  constructor(private http : HttpClient) { }

  uploadFile(file: File) : Observable<any> {
    const formData : FormData = new FormData();
    formData.append('file', file, file.name);

    const headers = new HttpHeaders({});

    return this.http.post(this.uploadUrl, formData, {headers: headers});
  }
  
}
