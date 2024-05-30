import { ComponentFixture, TestBed } from '@angular/core/testing';

import { StartViewComponent } from './start-view.component';

describe('StartViewComponent', () => {
  let component: StartViewComponent;
  let fixture: ComponentFixture<StartViewComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [StartViewComponent]
    });
    fixture = TestBed.createComponent(StartViewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
