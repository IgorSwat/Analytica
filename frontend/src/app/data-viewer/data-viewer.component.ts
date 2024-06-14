import { Component } from '@angular/core';
import { DataService } from '../data.service';
import { DataVisualization } from '../models/data.model';
import { FeatureType, FeatureLabel } from '../models/feature-types';
import { trigger, state, style, transition, animate, query, stagger } from '@angular/animations';


@Component({
  selector: 'app-data-viewer',
  templateUrl: './data-viewer.component.html',
  styleUrls: ['./data-viewer.component.css'],
  animations: [
    trigger('listAnimation', [
      transition('* => *', [
        query(':enter', [
          style({ opacity: 0, transform: 'translateY(-15px)' }),
          stagger('50ms', [
            animate('300ms ease-out', style({ opacity: 1, transform: 'translateY(0)' }))
          ])
        ], { optional: true })
      ])
    ])
  ]
})


export class DataViewerComponent {
  // Main data container
  data: DataVisualization | null = null;

  // Dynamic feature properties
  featureLabels: FeatureLabel[] | null = null;
  featureStates: boolean[] | null = null;

  // Row selection input elements
  inputValue: string = '';  // Bidirectional binding with row selection input element, stores the current value from input
  lastInputValue: string = '';
  inputErrorFlag: boolean = false;   // If input is incorrect and data not loaded properly, marks input bar as red
  
  // GUI text elements
  infoText: string = "Przykład użycia:\n1-5, 20-40 (Wiersze 1-5 i 20-40)\n1-10, 12 (Wiersze 1-10 oraz 12-ty)\n# (Wszystkie wiersze)\n\n \
                      Domyślnie 100 pierwszych wierszy";


  // --------------
  // Initialization
  // --------------

  constructor(private dataService: DataService) { }

  ngOnInit() {
    this.loadData("xxxxx");
  }

  // ------------
  // API handlers
  // ------------

  loadData(selection: string) : void {
    this.dataService.getData(selection).subscribe({
      next: (data) => {
        this.data = data;
        this.featureLabels = this.data.types.map((value) => {return new FeatureLabel(<FeatureType>value);});
        this.featureStates = [...this.data.states];
        this.inputValue = data.selection;
        this.lastInputValue = this.inputValue;
        this.inputErrorFlag = data.error;
      },
      error: (err) => {
        console.error('Error fetching data:', err)
      }
    });
  }

  updateData() : void {
    if (this.featureLabels && this.featureStates) {
      this.dataService.updateData(this.featureLabels, this.featureStates).subscribe({
        next: (response) => {
          this.loadData(this.lastInputValue);
        },
        error: (err) => console.error('Error fetching data:', err)
      });
    }
  }

  downloadData() : void {
    if (this.data != null) {
      this.dataService.downloadData().subscribe({
        next: (response) => {
          // Create CSV file representation
          const file = new Blob([response], { type: 'text/csv' });
        
          // Create virtual link
          const link = document.createElement('a');
          link.href = window.URL.createObjectURL(file);
          link.download = 'data.csv';
          link.click();
        },
        error: (err) => console.error('Error fetching data:', err)
      });
    }
  }

  refreshData() : void {
    this.loadData(this.inputValue);
  }

  // --------------
  // Action methods
  // --------------

  switchColumnState(colID: number) : void {
    if (this.featureStates != null)
      this.featureStates[colID] = !this.featureStates[colID];
  }

  // -----------------------
  // Getters and comparators
  // -----------------------
  
  isDataChanged() : boolean {
    if (this.data != null && this.featureLabels != null) {
      for (let id = 0; id < this.data.types.length; id++) {
        if (this.isTypeMismatch(id) || this.isStateMismatch(id))
          return true;
      }
    }
    return false;
  }

  isAnyDataLoaded() : boolean {
    return this.data != null && this.data.data.length > 0;
  }

  hasDataRangeChanged() : boolean {
    return this.inputValue != this.lastInputValue;
  }

  isTypeMismatch(colID : number) : boolean {
    return this.featureLabels![colID].featureType != <FeatureType>this.data?.types[colID];
  }

  isStateMismatch(colID: number) : boolean {
    return this.featureStates![colID] != this.data?.states[colID];
  }
  
  isColumnActive(colID: number) : boolean {
    return this.featureStates![colID];
  }

  hasFeatureType(colID: number) : boolean {
    return this.featureLabels![colID].featureType != FeatureType.NONE;
  }

}
