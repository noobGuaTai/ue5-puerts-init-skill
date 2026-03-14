import * as UE from 'ue';
import { argv } from 'puerts';

// Get arguments passed from C++
const gameInstance = argv.getByName("GameInstance");

console.log('========================================');
console.log('Puerts TypeScript Loaded Successfully!');
console.log('GameInstance:', gameInstance);
console.log('========================================');
