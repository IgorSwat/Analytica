import { Component } from '@angular/core';
import { DataService } from '../data.service';
import { DataVisualization } from '../models/data.model';
import { FeatureType, FeatureLabel } from '../models/feature-types';
import { debounceTime, distinctUntilChanged } from 'rxjs/operators';
import { FormControl } from '@angular/forms';

@Component({
  selector: 'app-data-viewer',
  templateUrl: './data-viewer.component.html',
  styleUrls: ['./data-viewer.component.css']
})

export class DataViewerComponent {
  data: DataVisualization | null = null;

  featureLabels: FeatureLabel[] | null = null;
  noneType = FeatureType.NONE;

  inputValue = new FormControl('');          // Bidirectional binding with row selection input element, stores the current value from input
  lastInputValue: string = ''; // form control as string 
  inputErrorFlag: boolean = false;  // If input is incorrect and data not loaded properly, marks input bar as red
  
  infoText: string = "Przykład użycia:\n1-5, 20-40 (Wiersze 1-5 i 20-40)\n1-10, 12 (Wiersze 1-10 oraz 12-ty)\n# (Wszystkie wiersze)\n\n \
                      Domyślnie 100 pierwszych wierszy";

  constructor(private dataService: DataService) { }

  ngOnInit() {
    this.loadData();

    this.inputValue.valueChanges.pipe(
      distinctUntilChanged() // Only unique values
    ).subscribe(value => {
      if (value !== null) {
        this.onRefresh(value);
      }
    });
    
  }

  loadData(selection: string = "") : void {
    this.dataService.getData(selection).subscribe({
      next: (data) => {
        this.data = data;
        this.loadFeatureTypes(data);
        this.inputErrorFlag = data.error;
      },
      error: (err) => console.error('Error fetching data:', err),
    });
  }

  updateData() : void {
    if (this.featureLabels) {
      this.dataService.updateData(this.featureLabels).subscribe({
        next: (response) => {
          this.loadData(this.lastInputValue);
        },
        error: (err) => console.error('Error fetching data:', err)
      });
    }
  }

  onRefresh(newValue: string) : void {
    if (newValue !== this.lastInputValue) {
      this.lastInputValue = newValue;
      this.loadData(newValue);
    }
  }

  isTypeMismatch(colID : number) : boolean {
    return this.data != null && this.featureLabels != null && this.featureLabels[colID].featureType != <FeatureType>this.data.types[colID];
  }

  isDataChanged() : boolean {
    if (this.data != null && this.featureLabels != null) {
      for (let id = 0; id < this.data.types.length; id++) {
        if (this.isTypeMismatch(id))
          return true;
      }
    }
    return false;
  }

  private loadFeatureTypes(data: DataVisualization) : void {
    this.featureLabels = new Array<FeatureLabel>();
    for (let type of data.types)
      this.featureLabels.push(new FeatureLabel(<FeatureType>type));
  }
  
}
