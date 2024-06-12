import { Component } from '@angular/core';
import { DataService } from '../data.service';
import { DataNormalization } from '../models/data.model';
import { trigger, state, style, transition, animate, query, stagger } from '@angular/animations';
@Component({
  selector: 'app-data-normalization',
  templateUrl: './data-normalization.component.html',
  styleUrls: ['./data-normalization.component.css'],
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
    ]),
    trigger('slideUpDown', [
      state('expanded', style({
        height: '*',
        opacity: 1,
        padding: '10px'
      })),
      state('collapsed', style({
        height: '0',
        opacity: 0,
        padding: '0 10px'
      })),
      transition('expanded <=> collapsed', [
        animate('300ms ease-in-out')
      ])
    ]),
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
export class DataNormalizationComponent {
  normalizedData: DataNormalization | null = null;
  numericMethod: string = 'standard';
  errorMessage: string = '';
  isFormExpanded: boolean = true;

  dataTableHeight: string = "450px";

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

  toggleForm() {
    this.isFormExpanded = !this.isFormExpanded;
    this.dataTableHeight = this.isFormExpanded ? "450px" : "600px";
  }
  

  
}
