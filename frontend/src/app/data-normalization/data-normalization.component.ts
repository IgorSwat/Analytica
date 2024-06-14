import { Component } from '@angular/core';
import { DataService } from '../data.service';
import { DataNormalization } from '../models/data.model';
import { FormControl } from '@angular/forms';
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
    ])
  ]
})


export class DataNormalizationComponent {
  // Main data container
  normalizedData: DataNormalization | null = null;

  // Numeric method selection elements
  numericMethod: string = '';
  prevNumericMethod: string = 'standard';
  availableMethods : string[] = ["standard", "min-max", "robust"];

  // Other GUI elements
  infoText1: string = "Wybór typu normalizacji zmiennych numerycznych.\n\n" + 
                      "Dla zmiennych kategorycznych w każdym przypadku stosowany jest one-hot encoding.";


  // --------------
  // Initialization
  // --------------

  constructor(private dataService: DataService) {}

  ngOnInit() {
    this.loadNormalizedData();
  }


  // ------------
  // API handlers
  // ------------

  loadNormalizedData(): void {
    this.dataService.getNormalizedData(this.numericMethod).subscribe({
      next: (data) => {
        this.normalizedData = data;
        this.numericMethod = data.numericMethod;
        this.prevNumericMethod = this.numericMethod;
      },
      error: (err) => console.error('Error fetching data:', err)
    });
  }


  // --------------
  // Action methods
  // --------------


  // -----------------------
  // Getters and comparators
  // -----------------------

  hasNumericMethodChanged() : boolean {
    return this.numericMethod != this.prevNumericMethod;
  }

}
