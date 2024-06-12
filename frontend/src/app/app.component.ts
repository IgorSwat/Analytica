import { Component } from '@angular/core';
import { trigger, transition, style, query, group, animate } from '@angular/animations';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  animations: [
    trigger('routeAnimations', [
      transition('OnePage <=> AnotherPage', [
        style({ position: 'relative' }),
        query(':enter, :leave', [
          style({
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%'
          })
        ]),
        query(':enter', [
          style({ left: '100%' })
        ]),
        query(':leave', [
          style({ left: '0%' })
        ]),
        group([
          query(':leave', [
            animate('300ms ease-out', style({ left: '-100%' }))
          ]),
          query(':enter', [
            animate('300ms ease-out', style({ left: '0%' }))
          ])
        ])
      ])
    ])
  ]
})
export class AppComponent {
  title = 'frontend';
  prepareRoute(outlet: RouterOutlet) {
    return outlet && outlet.activatedRouteData && outlet.activatedRouteData['animation'];
  }
}
