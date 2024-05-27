import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})

export class AppStateService {
  // False means disabled
  // You can unlock to test some buttons
  private navButtonsState = new BehaviorSubject<{ [key: string]: boolean}>({
    "nav-data": false,
    "nav-normalize": false,
    "nav-pca": false,
    "nav-stats": false
  });
  public navButtonsState$ = this.navButtonsState.asObservable();

  constructor() { }

  setNavButtonState(buttonName: string, state: boolean) : void {
    const currentState = this.navButtonsState.value;
    if (!(buttonName in currentState)) {
      console.error(`Invalid button name: ${buttonName}`);
      return;
    }

    this.navButtonsState.next({ ...currentState, [buttonName]: state});
  }

  getNavButtonState(buttonName: string) : boolean {
    const currentState = this.navButtonsState.value;
    if (!(buttonName in currentState)) {
      console.error(`Invalid button name: ${buttonName}`);
      return false;
    }

    return currentState[buttonName];
  }
}
