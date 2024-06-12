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
    { name: 'nav-data', label: 'Dane', route: '/data', active: true},
    { name: 'nav-normalize', label: 'Normalizacja', route: '/normalize', active: false},
    { name: 'nav-pca', label: 'PCA', route: '/pca', active: false},
    // { name: 'nav-stats', label: 'Statystyki', route: '/stats', active: false}
    { name: 'nav-stats', label: 'Statystyki', route: '/cluster', active: false}
  ];
  navButtonsState: { [key: string]: boolean} = {};

  constructor(private router: Router, private appStateService : AppStateService) {}

  ngOnInit(): void {
    this.appStateService.navButtonsState$.subscribe(state => {this.navButtonsState = state;});
  }

  navigateTo(route: string): void {
    this.router.navigate([route]);
    this.navButtons.forEach(button => {button.active = (button.route == route);})
  }

  isButtonDisabled(buttonName: string) : boolean {
    return !this.navButtonsState[buttonName] ?? false;
  }
}
