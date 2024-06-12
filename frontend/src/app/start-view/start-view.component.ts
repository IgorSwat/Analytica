import { Component, ElementRef, ViewChild } from '@angular/core';
import { FileUploadService } from '../file-upload.service'
import { AppStateService } from '../app-state.service';
import { Router } from '@angular/router';
@Component({
  selector: 'app-start-view',
  templateUrl: './start-view.component.html',
  styleUrls: ['./start-view.component.css']
})
export class StartViewComponent {
  @ViewChild('fileInput', {static: false}) fileInput!: ElementRef;

  constructor(private appStateService : AppStateService, private fileUploadService : FileUploadService, private router: Router) {}

  onFileButtonClick(): void {
    this.fileInput.nativeElement.click();
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      const file = input.files[0];
      this.uploadFile(file);

      // Just a test code
      //this.appStateService.setNavButtonState("nav-data", true);
      //this.appStateService.setNavButtonState("nav-pca", true);
    }
  }

  uploadFile(file: File): void {
    this.fileUploadService.uploadFile(file).subscribe(response => {
      console.log('File uploaded successfully', response);
      // Here redirect to /data route and unlock some buttons
      this.router.navigate(['/data']);
      this.appStateService.setNavButtonState('nav-data', true);
      this.appStateService.setNavButtonState('nav-normalize', true);
      
      // For tests
      this.appStateService.setNavButtonState('nav-pca', true);
      this.appStateService.setNavButtonState('nav-stats', true);
    }, error => {
      console.error('Error uploading file', error);
    });
  }
}
