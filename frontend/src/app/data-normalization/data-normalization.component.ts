import { Component } from '@angular/core';
import { DataService } from '../data.service';
import { DataNormalization } from '../models/data.model';

@Component({
  selector: 'app-data-normalization',
  templateUrl: './data-normalization.component.html',
  styleUrls: ['./data-normalization.component.css']
})
export class DataNormalizationComponent {
  normalizedData: DataNormalization | null = null;
  numericMethod: string = 'standard';
  errorMessage: string = '';
  constructor(private dataService: DataService) {
   }

   getNormalizedData(): void {
    this.dataService.getNormalizedData(this.numericMethod).subscribe(
      (data: DataNormalization) => {
        this.normalizedData = data;
        this.errorMessage = '';
      },
      (error) => {
        this.errorMessage = 'Error fetching normalized data';
        console.error(error);
      }
    );
  }

  
}
