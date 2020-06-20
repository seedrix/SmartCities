export class Shop {
    name: string;
    people: number;
    maxPeople: number;
    isStop: boolean;
    waitingTime: number;

    constructor(name: string, people: number, maxPeople: number) {
        this.name = name;
        this.people = people;
        this.maxPeople = maxPeople;

        if (this.people >= this.maxPeople) {
            this.isStop = true
        } else {
            this.isStop = false
        }
    }
}