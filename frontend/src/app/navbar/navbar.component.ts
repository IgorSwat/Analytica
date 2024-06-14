import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AppStateService } from '../app-state.service';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css']
})


export class NavbarComponent {

  // "name" attribute is a common identifier used for specyfic button (specifically inside AppStateService)
  navButtons = [
    { name: 'nav-data', label: 'Dane', route: '/data'},
    { name: 'nav-normalize', label: 'Normalizacja', route: '/normalize'},
    { name: 'nav-pca', label: 'PCA', route: '/pca'},
    { name: 'nav-clusters', label: 'Klasteryzacja', route: '/cluster'}
  ];
  navButtonsState: { [key: string]: boolean} = {};


  // --------------
  // Initialization
  // --------------

  constructor(private router: Router, private appStateService : AppStateService) {}

  ngOnInit(): void {
    this.appStateService.updateNavbarState();
    this.appStateService.navButtonsState$.subscribe(state => {this.navButtonsState = state;});
  }


  // --------------
  // Action methods
  // --------------

  navigateTo(route: string): void {
    this.router.navigate([route]);
  }


  // -----------------------
  // Getters and comparators
  // -----------------------

  isButtonActive(buttonRoute: string) : boolean {
    return this.router.url == buttonRoute;
  }

  isButtonDisabled(buttonName: string) : boolean {
    return !this.navButtonsState[buttonName] ?? false;
  }
}
