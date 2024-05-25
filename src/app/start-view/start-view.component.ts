import { Component, ElementRef, ViewChild } from '@angular/core';
import { FileUploadService } from '../file-upload.service'

@Component({
  selector: 'app-start-view',
  templateUrl: './start-view.component.html',
  styleUrls: ['./start-view.component.css']
})
export class StartViewComponent {
  @ViewChild('fileInput', {static: false}) fileInput!: ElementRef;

  constructor(private fileUploadService : FileUploadService) {}

  onFileButtonClick(): void {
    this.fileInput.nativeElement.click();
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      const file = input.files[0];
      this.uploadFile(file);
    }
  }

  uploadFile(file: File): void {
    this.fileUploadService.uploadFile(file).subscribe(response => {
      console.log('File uploaded successfully', response);
    }, error => {
      console.error('Error uploading file', error);
    });
  }
}
