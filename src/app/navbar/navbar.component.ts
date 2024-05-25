import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css']
})


export class NavbarComponent {
  navButtons = [
    { label: 'Dane', route: '/data', active: true, disabled: false },
    { label: 'Normalizacja', route: '/normalize', active: false, disabled: false },
    { label: 'PCA', route: '/pca', active: false, disabled: true },
    { label: 'Statystyki', route: '/stats', active: false, disabled: true }
  ];

  constructor(private router: Router) {}

  navigateTo(route: string): void {
    this.router.navigate([route]);
  }
}
