const fs = require('fs');
const path = require('path');

const GLB_PATH = path.join(__dirname, 'frontend', 'public', 'model', 'web amala.glb');

try {
    const data = fs.readFileSync(GLB_PATH);
    const glbString = data.toString('utf-8');
    
    const startIdx = glbString.indexOf('{"asset"');
    if (startIdx !== -1) {
        let openBraces = 0;
        let jsonEndStr = '';
        for (let i = startIdx; i < glbString.length; i++) {
            if (glbString[i] === '{') openBraces++;
            if (glbString[i] === '}') openBraces--;
            if (openBraces === 0) {
                jsonEndStr = glbString.substring(startIdx, i + 1);
                break;
            }
        }
        
        try {
            const json = JSON.parse(jsonEndStr);
            const meshes = json.meshes || [];
            const targets = new Set();
            meshes.forEach(mesh => {
                if (mesh.extras && mesh.extras.targetNames) {
                    mesh.extras.targetNames.forEach(tn => targets.add(tn));
                }
            });
            console.log("Found Target Names:", Array.from(targets).slice(0, 50)); // Print first 50
            if (targets.size > 50) console.log(`...and ${targets.size - 50} more.`);
        } catch (e) {
            console.error("Parse error:", e);
        }
    }
} catch (err) {
    console.error(err);
}
