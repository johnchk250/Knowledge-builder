/* Continuous, visual-first navigation over the accepted plant graph. */
'use strict';
const PlantScene=(()=>{
  const M=PlantSceneModel;
  let p,api,s,cleanup,viewport={x:0,y:0,w:1200,h:720},viewKey='',lastPick='';
  const q=()=>new URLSearchParams(location.hash.split('?')[1]||'');
  const h=()=>q().get('pick');
  const safe=x=>esc(x??'');
  const url=changes=>{const v=q();for(const[k,x]of Object.entries(changes)){if(x===null||x===undefined||x==='')v.delete(k);else v.set(k,x);}return '#overview'+(v.size?'?'+v:'');};
  const home='#overview';
  const areaURL=area=>'#overview?area='+encodeURIComponent(area);
  const openURL=id=>{let trail=(q().get('trail')||'').split(',').filter(x=>p.entities.has(x));if(trail.includes(id))trail=trail.slice(0,trail.indexOf(id));else if(s.id&&s.id!==id&&(p.assembly(s.id).some(n=>n.id===id)||s.nodes.some(n=>n.id===id&&n.role==='located'))){if(!trail.includes(s.id))trail.push(s.id);}else trail=[];return url({equipment:id,pick:null,edge:null,tab:null,view:null,trail:trail.slice(-12).join(','),browse:null,scene:null,layer:null,spread:null,opmode:null});};
  const pickURL=id=>url({pick:id,edge:null,browse:null});
  const source=(a,title='Source ↗')=>a.evidence?.length?`<button class="ps-source" data-action="fact-source" data-id="${safe(a.id)}" data-support="0">${safe(title)}</button>`:'';
  const nice=PlantExplorerModel.pretty;
  const text=(x,y,t,cls='ps-label',anchor='middle')=>`<text x="${x}" y="${y}" text-anchor="${anchor}" class="${cls}">${safe(t)}</text>`;
  function lines(label,max=25){const words=label.split(/\s+/),out=[''];for(const w of words){if((out.at(-1)+' '+w).trim().length>max&&out.at(-1))out.push(w);else out[out.length-1]=(out.at(-1)+' '+w).trim();}return out;}
  function short(n){const root=s.id?p.entities.get(s.id)?.label:'';if(n.label.startsWith(root+' '))return n.label.slice(root.length+1);const tag=root.match(/^[A-Z]{2,5}-\d+[AB]?\b/)?.[0];return tag&&n.label.startsWith(tag+' ')?n.label.slice(tag.length+1):n.label;}
  function symbol(kind,x,y,w=180,height=120){return `<svg x="${x}" y="${y}" width="${w}" height="${height}" viewBox="0 0 180 120" aria-hidden="true"><use href="#ps-${kind}"/></svg>`;}
  function defs(){return `<defs>
    <symbol id="ps-mechanical-part" viewBox="0 0 180 120"><path d="M12 61H168" class="ps-shaft"/><path d="M65 32H115V92H65Z" class="ps-metal"/><ellipse cx="115" cy="62" rx="16" ry="30" class="ps-metal"/><circle cx="115" cy="62" r="9" class="ps-wheel"/><path d="M41 92V106H75M144 86V106H109" class="ps-floor"/></symbol>
    <symbol id="ps-marker" viewBox="0 0 180 120"><path d="M20 105V17H142V104M62 17V46M58 43H106L116 86Q83 115 49 86Z" class="ps-metal"/><path d="M66 38H101M51 86H115" class="ps-shaft"/></symbol>
    <pattern id="ps-grid" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".8" fill="#cbd7d4"/></pattern>
    <linearGradient id="ps-metal" x2="0" y2="1"><stop stop-color="#ecf3f0"/><stop offset="1" stop-color="#b5c9c4"/></linearGradient>
    <linearGradient id="ps-coal" x2="0" y2="1"><stop stop-color="#607272"/><stop offset="1" stop-color="#354b4c"/></linearGradient>
    <marker id="ps-arrow" markerWidth="7" markerHeight="7" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6" fill="#ab7337"/></marker>
    <marker id="ps-water-arrow" markerWidth="7" markerHeight="7" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6" fill="#4388a3"/></marker>
    <marker id="ps-drive-arrow" markerWidth="7" markerHeight="7" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6" fill="#7e69a0"/></marker>
    <symbol id="ps-conveyor" viewBox="0 0 180 120"><path class="ps-metal" d="M19 88L19 102M63 76L63 103M111 60L111 103M157 49L157 102M13 103H168M19 88L63 102L63 76L111 103L111 61L157 102"/><path d="M22 80L150 39Q166 37 169 47Q172 57 158 62L30 102Q14 105 11 93Q8 84 22 80Z" fill="#8a9f99" stroke="#3d6460" stroke-width="2"/><path d="M23 84L153 43M29 97L160 57" class="ps-belt-line"/><circle cx="22" cy="91" r="7" class="ps-metal"/><circle cx="158" cy="50" r="7" class="ps-metal"/><path d="M50 77L55 89M79 68L84 79M107 59L112 70M135 50L140 61" stroke="#dce7df" stroke-width="3"/><path d="M38 78L54 66L65 70L74 60L91 61L108 48L121 52L139 38L150 41" fill="none" stroke="#364c49" stroke-width="5"/></symbol>
    <symbol id="ps-belt" viewBox="0 0 180 120"><path d="M30 51L130 25Q164 37 153 63L54 102Q20 93 30 51Z" fill="#5f8070" stroke="#3d6352" stroke-width="3"/><path d="M40 52L133 33Q151 43 143 58L51 94Q32 85 40 52Z" fill="#d7e1d2" stroke="#829e88" stroke-width="2"/><path d="M46 53L130 41M49 83L135 54" stroke="#344e3d" stroke-width="8"/></symbol>
    <symbol id="ps-idler" viewBox="0 0 180 120"><path d="M12 104H166M21 97V65M154 98V65" stroke="#799783" stroke-width="5"/><path d="M24 45L58 82M62 84H116M119 81L151 44" stroke="#628974" stroke-width="16"/><path d="M22 45L57 82M64 84H114M121 81L153 44" stroke="#b7cbbb" stroke-width="6"/></symbol>
    <symbol id="ps-scraper" viewBox="0 0 180 120"><path d="M28 36H153L127 74H48Z" fill="#c7b385" stroke="#96824e" stroke-width="3"/><path d="M40 64H137L126 83H48Z" fill="#6c8973" stroke="#54715d" stroke-width="2"/><path d="M20 88H163M37 75V105M145 74V105" stroke="#75947b" stroke-width="5"/></symbol>
    <symbol id="ps-takeup" viewBox="0 0 180 120"><path d="M36 109V15H142V109M38 15L141 109M141 15L39 109" fill="none" stroke="#8da88d" stroke-width="3"/><circle cx="90" cy="43" r="20" class="ps-metal"/><path d="M70 44V69H110V44M90 70V88" fill="none" stroke="#607d63" stroke-width="3"/><path d="M64 87H116V107H64Z" fill="#b8c6aa" stroke="#718469" stroke-width="2"/></symbol>
    <symbol id="ps-shaft-coupling" viewBox="0 0 180 120"><path d="M8 66H173" stroke="#51715f" stroke-width="9"/><ellipse cx="65" cy="65" rx="18" ry="33" class="ps-metal"/><path d="M64 32H113V98H64Z" fill="#95b099" stroke="#56785f" stroke-width="2"/><ellipse cx="114" cy="65" rx="18" ry="33" fill="#c5d5bf" stroke="#56785f" stroke-width="2"/><path d="M77 35V95M101 35V95" stroke="#55755e" stroke-width="3"/><circle cx="118" cy="44" r="3" fill="#55755e"/><circle cx="118" cy="86" r="3" fill="#55755e"/></symbol>
    <symbol id="ps-pile" viewBox="0 0 180 120"><ellipse cx="92" cy="103" rx="80" ry="10" fill="#d8e1dc"/><path d="M10 100L48 56L77 35L106 48L132 70L171 100Z" fill="url(#ps-coal)" stroke="#354e4c" stroke-width="2"/><path d="M48 56L83 73L106 48M77 35L83 73L55 99M83 73L132 70L117 100" fill="none" stroke="#96aaa1" stroke-opacity=".5"/></symbol>
    <symbol id="ps-shed" viewBox="0 0 180 120"><path d="M13 103V50Q90 -10 168 50V103M13 50H168M37 38V103M62 26V103M90 21V103M118 27V103M145 38V103" fill="none" stroke="#8ba49b" stroke-width="3"/><path d="M13 50Q90 -10 168 50L149 62Q90 9 32 62Z" fill="#dfe9e2" fill-opacity=".7" stroke="#829c91"/></symbol>
    <symbol id="ps-stacker" viewBox="0 0 180 120"><path d="M15 104H171M26 111H166" stroke="#94aaa1" stroke-width="3"/><path d="M52 94V48H75V94M51 62L155 22L160 35L75 77Z" class="ps-metal"/><path d="M63 65L86 57L82 72L104 49L99 65L123 42L119 57L147 33" fill="none" stroke="#547b70" stroke-width="2"/><path d="M58 48V22L152 24M59 24L115 51M62 31L19 73" fill="none" stroke="#829b91" stroke-width="2"/><rect x="42" y="82" width="47" height="18" rx="3" fill="#4c8276"/><rect x="39" y="51" width="23" height="20" class="ps-window"/><circle cx="50" cy="103" r="6" class="ps-wheel"/><circle cx="80" cy="103" r="6" class="ps-wheel"/><path d="M154 37L155 60" stroke="#b6874b" stroke-dasharray="4 4" stroke-width="3"/></symbol>
    <symbol id="ps-reclaimer" viewBox="0 0 180 120"><path d="M9 109H173M19 113H165" stroke="#a8b9ad" stroke-width="2"/><path d="M23 103L47 17H133L158 103M33 73H149M47 17L66 46H116L133 17M48 18L55 77M132 18L127 77" fill="none" stroke="#527e72" stroke-width="6"/><path d="M41 95L90 50L138 95" fill="none" stroke="#c49c5d" stroke-width="9"/><path d="M43 94L89 53L136 94" fill="none" stroke="#5e6d61" stroke-width="3" stroke-dasharray="3 5"/><path d="M74 21V65M107 21V66" stroke="#879d94" stroke-width="2"/><circle cx="23" cy="104" r="7" class="ps-wheel"/><circle cx="158" cy="104" r="7" class="ps-wheel"/></symbol>
    <symbol id="ps-transfer" viewBox="0 0 180 120"><path d="M40 108V22L90 8L144 22V108M40 22H144M40 63H144M40 102H144M62 24V100M122 24V100" fill="#e5ece5" fill-opacity=".65" stroke="#7c998d" stroke-width="2"/><path d="M9 36H84V60H105V86H166" fill="none" stroke="#5c8475" stroke-width="13"/><path d="M9 32H88V59H109V82H166" fill="none" stroke="#c59a60" stroke-width="3"/><path d="M48 18L89 5L143 18M150 110V33M145 39H157M145 51H157M145 63H157M145 75H157M145 87H157M145 99H157" fill="none" stroke="#789384" stroke-width="2"/></symbol>
    <symbol id="ps-building" viewBox="0 0 180 120"><path d="M29 105V35L90 11L150 35V105ZM29 35H150" class="ps-metal"/><rect x="49" y="49" width="23" height="23" class="ps-window"/><rect x="104" y="49" width="24" height="23" class="ps-window"/><path d="M76 105V80H104V105" class="ps-metal"/></symbol>
    <symbol id="ps-motor" viewBox="0 0 180 120"><rect x="25" y="39" width="112" height="54" rx="14" fill="#5b9281" stroke="#335e53" stroke-width="2"/><ellipse cx="135" cy="66" rx="14" ry="27" fill="#a5c2b5" stroke="#335e53" stroke-width="2"/><path d="M145 66H171" stroke="#496b61" stroke-width="9"/><path d="M42 43V87M53 43V87M64 43V87M75 43V87M86 43V87M97 43V87M108 43V87" stroke="#b7d0bc" stroke-width="3"/><path d="M32 96H58M107 96H133" stroke="#325d50" stroke-width="7"/><rect x="58" y="27" width="37" height="16" rx="3" class="ps-metal"/></symbol>
    <symbol id="ps-coupling" viewBox="0 0 180 120"><path d="M8 70H174" stroke="#527264" stroke-width="10"/><path d="M53 32Q88 10 123 32V95Q88 113 53 95Z" fill="#d2b777" stroke="#8b7954" stroke-width="2"/><ellipse cx="123" cy="64" rx="17" ry="35" fill="#e2cd9a" stroke="#8b7954" stroke-width="2"/><ellipse cx="122" cy="64" rx="8" ry="18" class="ps-metal"/><path d="M68 26V100M82 23V103M96 25V99" stroke="#aa905b" stroke-width="2"/><path d="M82 27V12H110V35" fill="none" stroke="#8b7954" stroke-width="3"/></symbol>
    <symbol id="ps-gearbox" viewBox="0 0 180 120"><path d="M33 99V34L120 21L149 42V96L62 109Z" fill="#d5e1d6" stroke="#6b8877" stroke-width="2"/><path d="M33 34L62 54L149 42M62 54V109" fill="none" stroke="#6b8877" stroke-width="2"/><circle cx="98" cy="73" r="23" fill="#a8bca9" stroke="#5c7a66" stroke-width="5" stroke-dasharray="7 3"/><circle cx="98" cy="73" r="8" class="ps-metal"/><path d="M12 60H39M139 72H170" stroke="#527264" stroke-width="9"/><path d="M68 111H147" stroke="#527264" stroke-width="5"/></symbol>
    <symbol id="ps-drive" viewBox="0 0 180 120"><svg x="0" y="27" width="80" height="80" viewBox="0 0 180 120"><use href="#ps-motor"/></svg><svg x="68" y="30" width="52" height="73" viewBox="0 0 180 120"><use href="#ps-coupling"/></svg><svg x="105" y="18" width="80" height="91" viewBox="0 0 180 120"><use href="#ps-gearbox"/></svg><path d="M9 107H178" stroke="#809789" stroke-width="3"/></symbol>
    <symbol id="ps-pulley" viewBox="0 0 180 120"><path d="M40 28L127 16V95L40 109Z" fill="#a9bfb0" stroke="#4a7160" stroke-width="2"/><ellipse cx="126" cy="56" rx="24" ry="40" fill="#789b83" stroke="#4a7160" stroke-width="2"/><path d="M132 57H169M8 68H40" stroke="#476953" stroke-width="9"/><ellipse cx="41" cy="68" rx="20" ry="40" fill="#d2dfd2" stroke="#4a7160" stroke-width="2"/><path d="M63 25V105M89 22V101M115 19V96" stroke="#779c80" stroke-width="2"/></symbol>
    <symbol id="ps-brake" viewBox="0 0 180 120"><circle cx="84" cy="58" r="34" class="ps-metal"/><circle cx="84" cy="58" r="9" class="ps-wheel"/><path d="M51 29L40 64L65 93M117 29L128 64L103 93M65 93H143V48" fill="none" stroke="#b98853" stroke-width="9"/><rect x="135" y="36" width="18" height="33" rx="3" fill="#cfa971"/><path d="M42 105H155" stroke="#6a8371" stroke-width="4"/></symbol>
    <symbol id="ps-pump" viewBox="0 0 180 120"><path d="M90 28V13H144V29M36 67H10M99 96V108H158" fill="none" stroke="#6b9dac" stroke-width="11"/><circle cx="91" cy="64" r="37" fill="#c1d9d9" stroke="#4a858b" stroke-width="3"/><path d="M88 39Q115 42 111 66Q107 89 88 86Q65 83 70 63Q75 48 88 58Q98 65 88 72" fill="none" stroke="#4a858b" stroke-width="5"/></symbol>
    <symbol id="ps-cooler" viewBox="0 0 180 120"><rect x="30" y="20" width="120" height="83" rx="4" fill="#d0e0dc" stroke="#6b8a7d" stroke-width="3"/><path d="M41 31H139M41 41H139M41 51H139M41 61H139M41 71H139M41 81H139M41 91H139" stroke="#829e94" stroke-width="3"/><circle cx="91" cy="63" r="26" fill="#ecf1e9" fill-opacity=".75" stroke="#64877b"/><path d="M90 39L98 60L114 74L90 69L71 77L83 60Z" fill="#5d8778"/></symbol>
    <symbol id="ps-tank" viewBox="0 0 180 120"><path d="M40 32V93Q90 122 140 93V32Z" fill="#c3d8d5" stroke="#698f83" stroke-width="2"/><ellipse cx="90" cy="32" rx="50" ry="16" fill="#e0ebe3" stroke="#698f83" stroke-width="2"/><path d="M42 72Q90 94 138 72" fill="none" stroke="#759c96" stroke-width="3"/><path d="M141 89H167V102" fill="none" stroke="#598997" stroke-width="6"/></symbol>
    <symbol id="ps-direct-drive" viewBox="0 0 180 120"><path d="M30 68H174" class="ps-shaft"/><svg x="0" y="15" width="115" height="90" viewBox="0 0 180 120"><use href="#ps-motor"/></svg><svg x="103" y="28" width="70" height="75" viewBox="0 0 180 120"><use href="#ps-coupling"/></svg><path d="M9 107H178" stroke="#809789" stroke-width="3"/></symbol>
    <symbol id="ps-filter" viewBox="0 0 180 120"><path d="M21 55H66M112 55H160" stroke="#5d94a2" stroke-width="8"/><path d="M63 27H116V84L104 104H75L63 84Z" fill="#d8e6df" stroke="#6b9181" stroke-width="3"/><path d="M73 37L105 85M73 55L99 94M81 35L108 74M75 84L105 37M73 65L95 36M88 94L109 58" stroke="#8ea89a" stroke-width="2"/></symbol>
    <symbol id="ps-sensor" viewBox="0 0 180 120"><path d="M91 79V107M69 106H112" stroke="#9d7545" stroke-width="5"/><rect x="56" y="33" width="69" height="49" rx="7" fill="#efd8a9" stroke="#b0884a" stroke-width="2"/><circle cx="92" cy="57" r="16" fill="#fff4d5" stroke="#b0884a" stroke-width="2"/><path d="M92 58L101 47M58 39L43 18" stroke="#a07840" stroke-width="3"/></symbol>
    <symbol id="ps-protection" viewBox="0 0 180 120"><path d="M90 14L142 32V63Q139 94 90 112Q41 94 38 63V32Z" fill="#f0deba" stroke="#b39861" stroke-width="3"/><path d="M66 64L85 81L117 43" stroke="#947441" stroke-width="7" fill="none"/></symbol>
    <symbol id="ps-valve" viewBox="0 0 180 120"><path d="M18 77H163" stroke="#548c9d" stroke-width="8"/><path d="M47 48L126 99V49L47 100Z" fill="#a7cdd0" stroke="#52818a" stroke-width="3"/><path d="M87 76V27M63 26H112" stroke="#6f8271" stroke-width="5"/></symbol>
    <symbol id="ps-spray" viewBox="0 0 180 120"><path d="M90 108V45L105 31" stroke="#619baa" stroke-width="7" fill="none"/><path d="M100 21L117 38" stroke="#437d89" stroke-width="7"/><path d="M116 23L148 9M121 29L161 25M123 36L159 46M119 41L145 62" stroke="#70b4c2" stroke-width="3" stroke-dasharray="3 5"/></symbol>
    <symbol id="ps-water" viewBox="0 0 180 120"><use href="#ps-spray"/><path d="M9 103H88M20 103V72H65V103" fill="none" stroke="#79a4aa" stroke-width="5"/><circle cx="43" cy="88" r="10" fill="#cadfe1" stroke="#6b9ba4" stroke-width="2"/></symbol>
    <symbol id="ps-chute" viewBox="0 0 180 120"><path d="M36 13H117V45L145 80L111 110L77 69H36Z" fill="#d1decf" stroke="#77917c" stroke-width="3"/><path d="M47 17V55H82L120 101M115 45L82 55" fill="none" stroke="#9fb39c" stroke-width="3"/><path d="M69 21V43L92 61L117 89" fill="none" stroke="#b58f51" stroke-width="5" stroke-dasharray="5 5"/></symbol>
    <symbol id="ps-silo" viewBox="0 0 180 120"><path d="M37 29Q90 0 144 29V77L107 104H77L37 77Z" fill="#d2ddcd" stroke="#7d947b" stroke-width="2"/><path d="M37 29Q90 52 144 29M37 77Q90 99 144 77M45 80V112M136 83V112M80 105V115H108V104" fill="none" stroke="#7d947b" stroke-width="3"/></symbol>
    <symbol id="ps-crusher" viewBox="0 0 180 120"><path d="M38 18H142L124 49V105H54V49Z" fill="#d6dfce" stroke="#7d9276" stroke-width="3"/><circle cx="89" cy="69" r="25" fill="#aabd9d" stroke="#6b835e" stroke-width="5" stroke-dasharray="6 3"/><circle cx="89" cy="69" r="7" class="ps-wheel"/><path d="M64 88Q89 111 115 87" fill="none" stroke="#829179" stroke-width="3"/><path d="M77 106V116M105 106V116" stroke="#829179" stroke-width="5"/></symbol>
    <symbol id="ps-screen" viewBox="0 0 180 120"><path d="M25 34L155 54L144 90L16 70Z" fill="#d2ddca" stroke="#809776" stroke-width="3"/><path d="M31 43L145 61M28 53L144 70M44 41L39 65M68 45L63 69M91 49L86 73M114 53L109 77M139 57L134 81M25 76V110M144 94V110" stroke="#829476" stroke-width="3"/></symbol>
    <symbol id="ps-ship" viewBox="0 0 180 120"><path d="M7 77H165L147 105H33Z" fill="#87a999" stroke="#547467" stroke-width="2"/><path d="M34 73V51H61V73M102 75V18H114V75M108 19L160 11L164 25L116 39M127 16V60" fill="#d0dfd0" stroke="#698571" stroke-width="3"/><path d="M7 114Q30 104 55 114T103 114T171 114" fill="none" stroke="#8cb4b5" stroke-width="3"/></symbol>
    <symbol id="ps-reference" viewBox="0 0 180 120"><path d="M49 9H111L134 32V111H49Z" fill="#eef2e8" stroke="#809b7e" stroke-width="3"/><path d="M111 9V32H134M65 52H116M65 68H116M65 84H104" fill="none" stroke="#809b7e" stroke-width="3"/></symbol>
    <symbol id="ps-assembly" viewBox="0 0 180 120"><path d="M44 79V37L91 14L140 37V80L92 107Z" fill="#d8e4d6" stroke="#809b7e" stroke-width="2"/><path d="M44 37L91 61L140 37M91 61V107" fill="none" stroke="#809b7e" stroke-width="2"/><circle cx="92" cy="57" r="16" fill="#ecf2e8" stroke="#809b7e" stroke-width="2"/><path d="M83 57H101M92 48V66" stroke="#638465" stroke-width="3"/></symbol>
    <symbol id="ps-compressor" viewBox="0 0 180 120"><rect x="21" y="24" width="136" height="73" rx="9" class="ps-metal"/><path d="M29 102H150M36 97V108M142 97V108M157 48H172V22" stroke="#6b9dac" stroke-width="6" fill="none"/><circle cx="62" cy="61" r="22" class="ps-wheel"/><path d="M50 61H74M62 49V73M100 43H140M100 55H140M100 67H140M100 79H140" stroke="#638a88" stroke-width="4"/></symbol>
    <symbol id="ps-yard" viewBox="0 0 180 120"><use href="#ps-pile"/><svg x="67" y="-6" width="119" height="110" viewBox="0 0 180 120"><use href="#ps-stacker"/></svg></symbol>
    <symbol id="ps-mechanical" viewBox="0 0 180 120"><use href="#ps-conveyor"/></symbol>
    <marker id="ps-power-arrow" markerWidth="7" markerHeight="7" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6" fill="#507ba1"/></marker>
    <symbol id="ps-silo-house" viewBox="0 0 180 120"><path class="ps-building-frame" d="M12 115V15H168V115M12 55H168M12 100H168"/><svg x="15" y="12" width="75" height="100" viewBox="0 0 180 120"><use href="#ps-silo"/></svg><svg x="90" y="12" width="75" height="100" viewBox="0 0 180 120"><use href="#ps-silo"/></svg></symbol>
    <symbol id="ps-extractor" viewBox="0 0 180 120"><ellipse cx="90" cy="70" rx="70" ry="25" class="ps-metal"/><path d="M38 62L90 15L142 62Q90 95 38 62Z" fill="#d9c28f" stroke="#8c805f" stroke-width="2"/><path d="M58 80L89 96L125 79M83 90V115H105V90" class="ps-metal"/><path d="M25 74Q90 106 155 74" fill="none" stroke="#816c9d" stroke-width="5"/><path d="M20 94H52M129 94H164" stroke="#637869" stroke-width="8"/></symbol>
    <symbol id="ps-cone" viewBox="0 0 180 120"><path d="M18 92H162M90 33V113M28 48L151 110M153 48L27 110" stroke="#799381" stroke-width="5"/><path d="M37 81L90 12L143 81Q90 116 37 81Z" fill="#d8c395" stroke="#9b8963" stroke-width="2"/></symbol>
    <symbol id="ps-platform" viewBox="0 0 180 120"><ellipse cx="90" cy="64" rx="78" ry="40" class="ps-metal"/><ellipse cx="90" cy="64" rx="27" ry="15" fill="#546b61"/><path d="M18 84V112M162 84V112" stroke="#7b9582" stroke-width="5"/></symbol>
    <symbol id="ps-blade" viewBox="0 0 180 120"><ellipse cx="90" cy="66" rx="70" ry="38" fill="none" stroke="#beccb9" stroke-dasharray="5 5" stroke-width="3"/><g class="ps-rotor"><path d="M20 58L87 40L150 79L110 89L85 63L24 76Z" fill="#a8b8a3" stroke="#628269" stroke-width="3"/><circle cx="88" cy="62" r="10" class="ps-wheel"/></g></symbol>
    <symbol id="ps-bearing" viewBox="0 0 180 120"><ellipse cx="90" cy="64" rx="73" ry="39" fill="#b9c5ae" stroke="#7e7093" stroke-width="8" stroke-dasharray="8 3"/><ellipse cx="90" cy="64" rx="50" ry="23" fill="#f2f5e9" stroke="#738c71" stroke-width="3"/></symbol>
    <symbol id="ps-sleeve" viewBox="0 0 180 120"><path d="M30 33V89Q90 119 150 89V33" class="ps-metal"/><ellipse cx="90" cy="33" rx="60" ry="22" class="ps-metal"/><ellipse cx="90" cy="33" rx="44" ry="13" fill="#6b8475"/></symbol>
    <symbol id="ps-seal" viewBox="0 0 180 120"><ellipse cx="90" cy="64" rx="69" ry="36" fill="#c2cbb4" stroke="#758a71" stroke-width="5"/><ellipse cx="90" cy="64" rx="57" ry="28" fill="none" stroke="#758a71" stroke-width="3"/><ellipse cx="90" cy="64" rx="44" ry="20" fill="#f2f5e9" stroke="#758a71" stroke-width="4"/></symbol>
    <symbol id="ps-lubrication" viewBox="0 0 180 120"><rect x="55" y="45" width="69" height="58" rx="7" class="ps-metal"/><path d="M65 43V20H115V43M90 22V8M57 78H20V35M123 78H158V35" fill="none" stroke="#619baa" stroke-width="7"/><path d="M89 54Q70 79 90 85Q109 79 89 54" fill="#c5a567"/></symbol>
    <symbol id="ps-panel" viewBox="0 0 180 120"><rect x="43" y="10" width="94" height="101" rx="4" class="ps-metal"/><rect x="58" y="26" width="64" height="27" fill="#8eaaa0" stroke="#658477"/><path d="M64 72H75M94 72H105M64 87H105" stroke="#527b69" stroke-width="5"/></symbol>
    <symbol id="ps-fan" viewBox="0 0 180 120"><circle cx="90" cy="60" r="45" class="ps-metal"/><path d="M88 58Q43 18 68 22Q109 13 93 54Q145 37 129 68Q105 95 94 66Q70 111 55 83Q50 58 85 61Z" fill="#709b8b"/><circle cx="90" cy="60" r="9" class="ps-wheel"/><path d="M54 100H129" stroke="#607c67" stroke-width="6"/></symbol>
    <symbol id="ps-gate" viewBox="0 0 180 120"><path d="M58 8H122V40L163 92L128 114L90 68L52 114L17 92L58 40Z" class="ps-metal"/><path d="M59 26L101 68" stroke="#b0874b" stroke-width="7"/><circle cx="61" cy="28" r="8" fill="#698474"/></symbol>
    <symbol id="ps-feeder" viewBox="0 0 180 120"><path d="M15 45H150V83H15Z" class="ps-metal"/><rect x="10" y="77" width="155" height="23" rx="11" fill="#89a18d" stroke="#4e735b" stroke-width="3"/><path d="M22 102V115M148 102V115M24 52H143" stroke="#58795e" stroke-width="4"/><circle cx="24" cy="88" r="7" class="ps-wheel"/><circle cx="149" cy="88" r="7" class="ps-wheel"/></symbol>
    <symbol id="ps-access" viewBox="0 0 180 120"><path d="M27 112V15H153V112M19 15H162M76 17V66Q104 65 103 82Q96 103 80 90" fill="none" stroke="#8e9f84" stroke-width="7"/><path d="M24 45H46M24 67H46M24 89H46" stroke="#8e9f84" stroke-width="4"/></symbol>
    <symbol id="ps-duct" viewBox="0 0 180 120"><path d="M24 103V37Q24 17 45 17H159V48H63V103Z" class="ps-metal"/><path d="M35 93V40Q35 29 49 29H142" fill="none" stroke="#79a0a5" stroke-width="3" stroke-dasharray="8 6"/></symbol>
    <symbol id="ps-spray-system" viewBox="0 0 180 120"><use href="#ps-water"/></symbol>
    <symbol id="ps-crusher-housing" viewBox="0 0 180 120"><path d="M30 30L90 8L148 30V95L91 115L30 95Z" class="ps-metal"/><path d="M45 45L87 30V94L45 81Z" fill="#708b78"/><path d="M105 32L137 44V80L105 94Z" fill="#a7c1ad" stroke="#718f79" stroke-width="2"/><path d="M45 45L14 56V93L45 81" fill="#d8e6d6" stroke="#718f79" stroke-width="3"/></symbol>
    <symbol id="ps-damper" viewBox="0 0 180 120"><path d="M15 33H166V90H15Z" fill="#dce5da" stroke="#789282" stroke-width="3"/><path d="M44 35L69 87M87 35L112 87M130 35L154 87" stroke="#6c8875" stroke-width="6"/><path d="M91 33V16H132" fill="none" stroke="#789282" stroke-width="4"/><rect x="128" y="5" width="35" height="24" rx="5" class="ps-metal"/></symbol>
    <symbol id="ps-crusher-house" viewBox="0 0 180 120"><use href="#ps-transfer"/></symbol>
    <symbol id="ps-crusher-rotor" viewBox="0 0 180 120"><path d="M8 64H172" stroke="#6e7d6b" stroke-width="10"/><g class="ps-rotor"><circle cx="90" cy="64" r="37" fill="#d6bc88" stroke="#8d7853" stroke-width="3"/><circle cx="90" cy="64" r="26" fill="none" stroke="#b28e51" stroke-width="10" stroke-dasharray="7 5"/><path d="M90 28V100M54 64H126" stroke="#77674a" stroke-width="4"/><circle cx="90" cy="64" r="10" class="ps-wheel"/></g></symbol>
    <symbol id="ps-cage" viewBox="0 0 180 120"><path d="M25 29Q25 111 139 105L157 79Q57 85 49 20Z" class="ps-metal"/><path d="M32 48L54 40M42 67L67 57M57 83L80 72M77 95L94 82M99 103L112 85M120 105L130 85" stroke="#65836e" stroke-width="4"/></symbol>
    <symbol id="ps-foundation" viewBox="0 0 180 120"><path d="M12 32H168V52H12Z" class="ps-metal"/><path d="M26 56L43 64L26 71L43 78L26 85L43 92M75 56L92 64L75 71L92 78L75 85L92 92M128 56L145 64L128 71L145 78L128 85L145 92M12 99H168" fill="none" stroke="#7b8b74" stroke-width="4"/></symbol>
    <symbol id="ps-hydraulic" viewBox="0 0 180 120"><use href="#ps-lubrication"/><path d="M115 30H165V97" stroke="#68919f" stroke-width="6" fill="none"/></symbol>
    <symbol id="ps-cylinder" viewBox="0 0 180 120"><path d="M15 64H170" stroke="#687c70" stroke-width="10"/><rect x="38" y="47" width="72" height="33" class="ps-metal"/><path d="M56 48V27M95 48V27" stroke="#6498a2" stroke-width="5"/></symbol>
    <symbol id="ps-actuator" viewBox="0 0 180 120"><use href="#ps-cylinder"/><rect x="43" y="12" width="47" height="35" rx="6" class="ps-metal"/><circle cx="30" cy="31" r="15" fill="none" stroke="#728b73" stroke-width="3"/></symbol>
    <symbol id="ps-exciter" viewBox="0 0 180 120"><path d="M10 66H170" stroke="#728674" stroke-width="7"/><rect x="35" y="41" width="110" height="48" rx="15" class="ps-metal"/><circle cx="91" cy="64" r="28" fill="#ddc58e" stroke="#8c7851" stroke-width="3"/><path d="M65 62Q90 110 117 63Z" fill="#a38a55"/></symbol>
    <symbol id="ps-cyclone" viewBox="0 0 180 120"><path d="M48 17H135V56L100 98V116H82V98L48 56Z" class="ps-metal"/><path d="M90 17V4M15 30H49" stroke="#77959c" stroke-width="10"/><path d="M66 32Q136 38 66 51Q110 69 88 85" fill="none" stroke="#88a7a4" stroke-width="3"/></symbol>
    <symbol id="ps-de-house" viewBox="0 0 180 120"><use href="#ps-cyclone"/><svg x="75" y="40" width="95" height="80" viewBox="0 0 180 120"><use href="#ps-fan"/></svg></symbol>
    <symbol id="ps-de-stream" viewBox="0 0 180 120"><use href="#ps-de-house"/></symbol>
    <symbol id="ps-detector" viewBox="0 0 180 120"><path d="M23 98V20H151V98M23 34H151M23 87H151" stroke="#9a824f" stroke-width="9" fill="none"/><path d="M14 68H162" stroke="#6c8876" stroke-width="12"/><path d="M50 45Q90 70 130 45" stroke="#d2b572" stroke-dasharray="5 5" fill="none"/><rect x="151" y="31" width="23" height="43" rx="4" class="ps-metal"/></symbol>
    <symbol id="ps-weigher" viewBox="0 0 180 120"><path d="M12 53H167M28 94H151" stroke="#7c957e" stroke-width="7"/><path d="M35 63V90M142 63V90" stroke="#b39658" stroke-width="8"/><path d="M42 94L58 104L42 112M123 94L139 104L123 112" stroke="#9f8453" stroke-width="4" fill="none"/><g fill="#abc0ac" stroke="#658274" stroke-width="3"><circle cx="35" cy="53" r="10"/><circle cx="70" cy="53" r="10"/><circle cx="106" cy="53" r="10"/><circle cx="142" cy="53" r="10"/></g></symbol>
    <symbol id="ps-receiver" viewBox="0 0 180 120"><rect x="54" y="8" width="72" height="97" rx="30" class="ps-metal"/><path d="M57 99V116M122 99V116M15 43H54M126 43H165" stroke="#629baa" stroke-width="6"/><circle cx="90" cy="31" r="12" fill="#f6eed1" stroke="#a7915a" stroke-width="2"/></symbol>
    <symbol id="ps-pipe" viewBox="0 0 180 120"><path d="M12 85H85V32H165" stroke="#6099a7" stroke-width="12" fill="none"/><path d="M25 73V97M73 48H97M146 20V44" stroke="#407582" stroke-width="5"/></symbol>
  </defs>`;}
  function hotspot(n,x,y,w=160,height=106,opts={}){
    const labels=lines(opts.label||short(n),opts.max||26),selected=h()===n.id;
    const above=n.kind==='shed'&&s.kind==='yard'&&q().get('spread')!=='1',labelY=above?-15:height+17;
    const hint=n.role==='located'?'located here':n.role==='connected'?'connected '+nice(n.kind):nice(n.kind)+((p.children.get(n.id)||[]).length?' · explore parts →':' · inspect →');
    return `<g class="ps-hotspot ${selected?'is-selected':''} ${n.role==='connected'?'ps-external':''}" data-node="${safe(n.id)}" data-action="scene-pick" data-id="${safe(n.id)}" tabindex="0" role="button" aria-label="Inspect ${safe(n.label)}" transform="translate(${x} ${y})"><title>${safe(n.label)} · ${n.role==='located'?'Located here':n.role==='part'?'Part of '+s.title:'Select to explore'}</title><rect class="ps-halo" x="-10" y="-8" width="${w+20}" height="${height+labels.length*18+24}" rx="16"/>${symbol(n.kind==='drive'?M.driveSymbol(p,n.id):n.kind==='coupling'&&/low.speed|geared coupling|flexible coupling/i.test(n.label)?'shaft-coupling':n.kind,0,0,w,height)}${labels.map((t,i)=>text(w/2,labelY+i*18,t)).join('')}${text(w/2,above?-33:height+20+labels.length*18,hint,'ps-node-hint')}</g>`;
  }
  function routePath(a,b){const right=b.x>a.x,sy=a.y,ty=b.y,mx=(a.x+b.x)/2;return Math.abs(ty-sy)<25?`M${a.x} ${sy}C${mx} ${sy+2} ${mx} ${ty+2} ${b.x} ${ty}`:`M${a.x} ${sy}C${mx} ${sy} ${mx} ${ty} ${b.x} ${ty}`;}
  function edgeMarkup(edges,positions,routes=new Map()){return M.groupEdges(edges).map(e=>{
    const a=positions.get(e.from),b=positions.get(e.to);if(!a||!b)return '';
    const net=e.network,layer=q().get('layer')||'all';if(layer!=='all'&&net!==layer)return '';
    const d=routes.get(e.from+'>'+e.to)||(e.from===e.to?`M${a.x+a.w} ${a.y+a.h/2}C${a.x+a.w+55} ${a.y+a.h/2} ${a.x+a.w+55} ${a.y-25} ${a.x+a.w/2} ${a.y-25}V${a.y}`:routePath({x:a.x+(b.x>=a.x?a.w:0),y:a.y+a.h/2},{x:b.x+(b.x>=a.x?0:b.w),y:b.y+b.h/2}));
    return `<g class="ps-edge ps-edge-${safe(net)}"><path d="${d}" marker-end="url(#ps-${net==='utility'?'water-':net==='mechanical'?'drive-':net==='electrical'?'power-':''}arrow)"/><path class="ps-edge-hit" d="${d}" data-action="scene-edge" data-id="${safe(e.facts[0].id)}" tabindex="0" role="button" aria-label="Inspect ${safe(p.entities.get(e.from)?.label)} to ${safe(p.entities.get(e.to)?.label)} connection"/></g>`;
  }).join('');}
  function plant(){
    const stageKinds=['ship','screen','transfer','yard','conveyor','silo','crusher','conveyor','silo'];
    const pos=new Map(p.stages.map(st=>[st.id,{x:105+(st.col-1)*375,y:45+(st.row-1)*225,w:180,h:110}]));
    let paths=p.links.map(l=>{const a=pos.get(l.from),b=pos.get(l.to);if(!a||!b)return '';let d;
      if(a.y===b.y)d=routePath({x:a.x+(b.x>a.x?190:-10),y:a.y+75},{x:b.x+(b.x>a.x?-10:190),y:b.y+75});
      else if(a.x===b.x)d=`M${a.x+90} ${a.y+155}V${b.y-5}`;
      else d=`M${a.x+175} ${a.y+110}H${a.x+228}V${b.y-20}H${b.x+90}V${b.y-5}`;
      return `<g class="ps-edge ps-edge-material"><path d="${d}" marker-end="url(#ps-arrow)"/><path d="${d}" class="ps-edge-hit" data-action="plant-branch" data-id="${l.id}" tabindex="0" role="button" aria-label="Inspect ${safe(l.from)} to ${safe(l.to)} flow"/></g>`;}).join('');
    const path=p.paths.find(x=>x.id===q().get('path'));
    if(q().get('layer')&&!['all','material'].includes(q().get('layer')))paths='';
    return paths+p.stages.map((st,i)=>{const posn=pos.get(st.id);return `<a href="${areaURL(st.id)}" class="ps-stage-scene ${path&&!path.stages.includes(st.id)?'ps-dimmed':''}" aria-label="Explore ${safe(st.title)}"><g transform="translate(${posn.x} ${posn.y})"><rect class="ps-halo" x="-40" y="-6" width="265" height="185" rx="22"/>${text(-20,15,String(st.number).padStart(2,'0'),'ps-stage-index','start')}${symbol(stageKinds[i],0,0,180,115)}${text(90,144,st.title,'ps-stage-title')}${text(90,165,'Explore area →','ps-node-hint')}</g></a>`;}).join('');
  }
  function siloScene(){
    const positions=new Map(),routes=new Map(),drawn=new Map(),decor=[];
    const parts=s.nodes.filter(n=>n.role==='part'),byId=new Map(s.nodes.map(n=>[n.id,n]));
    const put=(id,x,y,w=160,h=95,title)=>{const n=byId.get(id);if(!n)return;const pos={x,y,w,h};positions.set(id,pos);drawn.set(id,{n,...pos,title});};
    const placeKind=(k,x,y,w,h)=>{const n=parts.find(n=>n.kind===k&&!drawn.has(n.id));if(n)put(n.id,x,y,w,h);};
    const pick=(pattern,x,y,w=150,h=95)=>{const n=parts.find(n=>pattern.test(n.label));if(n)put(n.id,x,y,w,h);};
    let height=840;
    if(s.kind==='silo-house'){
      const columns=M.siloColumns(p,s.id);height=970;
      decor.push(`<rect x="200" y="156" width="680" height="660" rx="9" class="ps-building-frame"/>`,text(220,179,'UEE-2 · SILO HOUSE','ps-zone-label','start'));
      decor.push(text(530,24,'RECEIVING FROM DISTRIBUTION & RECLAIM','ps-zone-label'),text(1005,110,'HOUSE SERVICES','ps-zone-label'));
      const levels=[[330,'STORAGE'],[466,'EXTRACTION'],[599,'BELT FEEDING'],[733,'ROUTE SELECTION']];
      for(const[y,title]of levels)decor.push(`<path d="M214 ${y}H866" class="ps-floor"/>`,text(184,y-20,title,'ps-zone-label','end'));
      columns.forEach((column,i)=>{
        const x=285+i*340;
        column.inlets.forEach((id,j)=>put(id,x-55+j*160,45,130,77));
        put(column.vessel,x,195,180,105);
        column.extractors.forEach((id,j)=>put(id,x+j*155,355,180,77));
        column.feeders.forEach((id,j)=>put(id,x+j*155,488,180,77));
        column.gates.forEach((id,j)=>put(id,x+15+j*140,622,150,72));
      });
      const gates=new Set(columns.flatMap(c=>c.gates));
      const outlets=[...new Set(s.edges.filter(a=>a.context.network==='material'&&gates.has(a.canonical_subject)).map(a=>a.canonical_object))].sort((a,b)=>p.entities.get(a).label.localeCompare(p.entities.get(b).label));
      outlets.forEach((id,i)=>put(id,285+i*340,830,180,80));
      decor.push(text(540,800,'SELECTED OUTLET → CRUSHER HOUSE','ps-zone-label'));
      const services=parts.filter(n=>!drawn.has(n.id));
      services.forEach((n,i)=>put(n.id,960,135+i*148,155,82,
        /Vent-Filter/.test(n.label)?'Silo vent filters':/Local DFDS/.test(n.label)?'DFDS · ten spray zones':/Service and drinking/.test(n.label)?'Service & drinking water':/Maintenance access/.test(n.label)?'Access & lifting':/Sump Pumps/.test(n.label)?'Sump pumps SP-7A / B':short(n)));
      height=Math.max(height,180+services.length*148);
    }else if(s.kind==='extractor'){
      decor.push(`<path d="M600 15V700" class="ps-assembly-leader"/>`,text(600,24,'INSIDE THE ROTARY EXTRACTOR','ps-zone-label'));
      placeKind('cone',500,48,200,117);placeKind('blade',505,220,190,75);
      placeKind('platform',500,342,200,73);pick(/Slew bearing and external gear$/,500,463,200,73);
      const chute=parts.find(n=>n.kind==='chute');if(chute)put(chute.id,530,586,140,90);
      pick(/Adjusting sleeve$/,875,55,165,100);pick(/Labyrinth seal$/,895,560,150,100);
      placeKind('lubrication',80,80,170,110);
      pick(/Common VFD$/,75,550,160,100);pick(/Local control station$/,920,225,155,95);
      const drives=parts.filter(n=>n.kind==='drive').sort((a,b)=>a.label.localeCompare(b.label));
      drives.forEach((n,i)=>{
        put(n.id,i?925:65,380,185,100);
        // Aggregate only the drawing positions, never the graph identities or
        // evidence. Selecting an arrow still names the actual motor/pinion.
        for(const a of p.children.get(n.id)||[])positions.set(a.canonical_subject,positions.get(n.id));
      });
      decor.push(text(600,779,'Each drive: motor → coupling → gearbox → pinion. Select a drive to open it.','ps-caption'));
    }else{
      positions.set(s.id,{x:460,y:190,w:280,h:285});
      decor.push(`<path class="ps-building-frame" d="M396 120H804V428L633 622H567L396 428Z"/>`,text(600,34,'VESSEL · VENTING · ACCESS · OUTLET','ps-zone-label'));
      const shell=parts.find(n=>/Shell and sloping liner$/.test(n.label));if(shell)put(shell.id,460,218,280,210);
      placeKind('filter',520,50,160,96);pick(/Level and temperature instruments$/,885,210,185,117);
      pick(/Manholes and access openings$/,85,212,190,115);pick(/Emergency bypass chute$/,885,478,175,113);
      const out=s.nodes.find(n=>n.role==='connected'&&n.kind==='extractor');if(out)put(out.id,510,639,180,95);
      decor.push(text(600,583,'COAL DISCHARGES TO THE EXTRACTOR BELOW','ps-zone-label'));
    }
    // Every unplaced owned part stays reachable on the canvas, including newly
    // accepted components that were not present when this template was written.
    const extra=parts.filter(n=>!drawn.has(n.id));
    extra.forEach((n,i)=>put(n.id,55+(i%5)*230,height+30+Math.floor(i/5)*190,160,100));
    if(extra.length)height+=60+Math.ceil(extra.length/5)*190;
    const edges=s.edges.filter(a=>positions.has(a.canonical_subject)&&positions.has(a.canonical_object)&&positions.get(a.canonical_subject)!==positions.get(a.canonical_object));
    for(const a of edges){
      const from=positions.get(a.canonical_subject),to=positions.get(a.canonical_object);
      if(a.context.network==='material'&&to.y>from.y){
        const x1=from.x+from.w/2,x2=to.x+to.w/2,y1=from.y+from.h,y2=to.y;
        routes.set(a.canonical_subject+'>'+a.canonical_object,`M${x1} ${y1}C${x1} ${y1+55} ${x2} ${y2-32} ${x2} ${y2}`);
      }
    }
    s.height=height;s.initialHeight=height;
    return decor.join('')+edgeMarkup(edges,positions,routes)+[...drawn.values()].map(n=>hotspot(n.n,n.x,n.y,n.w,n.h,{label:n.title})).join('');
  }
  function crusherSelection(){
    const columns=M.crusherColumns(p,s.id),index=Math.max(0,Math.min(columns.length-1,Number(q().get('line'))||0)),column=columns[index];
    const route=q().get('coalroute')==='bypass'?'bypass':'screen',outlet=column?.outlets.includes(q().get('outlet'))?q().get('outlet'):column?.outlets[0];
    return {columns,index,column,route,outlet};
  }
  function crusherRouteGuide(){
    if(s.kind==='transfer')return transferRouteGuide();
    if(s.kind!=='crusher-house'||q().get('scene')==='connections')return '';
    const v=crusherSelection();
    const group=(title,items,key,selected)=>`<div><span>${title}</span><nav aria-label="${title}">${items.map(([id,name])=>`<a href="${safe(url({[key]:id,pick:null,edge:null}))}" ${String(id)===String(selected)?'aria-current="true"':''}>${safe(name)}</a>`).join('')}</nav></div>`;
    return `<div class="ps-crusher-guide">${group('Follow a stream',v.columns.map((c,i)=>[i,c.inlets.map(x=>p.entities.get(x).label).join(' / ')||p.entities.get(c.crusher).label]),'line',v.index)}${group('Coal path',[['screen','Screen & crush'],['bypass','Direct bypass']],'coalroute',v.route)}${group('Selected outlet',(v.column?.outlets||[]).map(id=>[id,p.entities.get(id).label]),'outlet',v.outlet)}<small>Illustrate a route · no live status or commands</small></div>`;
  }
  function crusherHouseScene(){
    const v=crusherSelection(),positions=new Map(),drawn=new Map(),routes=new Map(),byId=new Map(s.nodes.map(n=>[n.id,n]));
    const put=(id,x,y,w=135,h=78,title)=>{const n=byId.get(id);if(n){positions.set(id,{x,y,w,h});drawn.set(id,{n,x,y,w,h,title});}};
    const decor=[`<rect x="195" y="170" width="665" height="675" rx="10" class="ps-building-frame"/>`,text(530,34,'FROM BLENDING SILO HOUSE · UEE-2','ps-zone-label'),text(1010,148,'HOUSE SERVICES','ps-zone-label')];
    // Vertical order follows the GA; coordinates are illustrative, not a scaled survey.
    for(const[y,title]of [[147,'+34.200 · INLET'],[381,'+24.000 · SCREEN'],[552,'+18.000 · CRUSHER'],[694,'+10.900 · FEEDER']])decor.push(`<path d="M213 ${y}H842" class="ps-floor"/>`,text(180,y-16,title,'ps-zone-label','end'));
    v.columns.forEach((c,i)=>{
      const x=275+i*340;
      c.inlets.forEach((id,j)=>put(id,x+j*148,55,145,75));
      c.inletGates.forEach((id,j)=>put(id,x+14+j*130,190,115,70));
      c.screens.forEach((id,j)=>put(id,x+j*155,305,145,75));
      put(c.crusher,x,437,145,85);
      c.feeders.forEach((id,j)=>put(id,x-12+j*160,603,170,70));
      c.outletGates.forEach((id,j)=>put(id,x+13+j*125,747,120,60));
      // Three routes stay visually distinct. Route endpoints are graph identities.
      for(const gate of c.inletGates)for(const feeder of c.feeders)routes.set(gate+'>'+feeder,`M${x+129} 222H${x+185}V624H${x+158}`);
      for(const screen of c.screens)for(const feeder of c.feeders)routes.set(screen+'>'+feeder,`M${x} 345H${x-32}V624H${x-12}`);
      decor.push(text(x+183,403,'BYPASS','ps-route-label'),text(x-38,480,'UNDERSIZE','ps-route-label','end'));
    });
    const outlets=[...new Set(v.columns.flatMap(c=>c.outlets))];outlets.forEach((id,i)=>put(id,283+i*330,890,160,78));
    decor.push(text(530,870,'TO UEF-13 · BUNKER FEED','ps-zone-label'));
    const services=s.nodes.filter(n=>n.role==='part'&&!drawn.has(n.id));
    services.forEach((n,i)=>put(n.id,925,187+i*157,175,82,/DE System/.test(n.label)?'Dust extraction · DE-1 / 2':/Local DFDS/.test(n.label)?'DFDS · six spray zones':/Maintenance access/.test(n.label)?'Access & lifting':/Service and drinking/.test(n.label)?'Water services':/Drainage sump/.test(n.label)?'Drainage sump & pumps':short(n)));
    const relevant=s.edges.filter(a=>a.context.network==='material'&&positions.has(a.canonical_subject)&&positions.has(a.canonical_object)&&a.canonical_subject!==s.id&&a.canonical_object!==s.id);
    for(const a of relevant){const k=a.canonical_subject+'>'+a.canonical_object;if(routes.has(k))continue;const from=positions.get(a.canonical_subject),to=positions.get(a.canonical_object);routes.set(k,`M${from.x+from.w/2} ${from.y+from.h}C${from.x+from.w/2} ${from.y+from.h+35} ${to.x+to.w/2} ${to.y-35} ${to.x+to.w/2} ${to.y}`);}
    const active=M.crusherRoute(p,v.column,v.route,v.outlet),keys=new Set(active.map(a=>a.canonical_subject+'>'+a.canonical_object));
    const inactive=relevant.filter(a=>!keys.has(a.canonical_subject+'>'+a.canonical_object));
    s.height=Math.max(1050,240+services.length*157);s.initialHeight=s.height;
    return decor.join('')+`<g class="ps-route-inactive">${edgeMarkup(inactive,positions,routes)}</g>`+edgeMarkup(active,positions,routes)+[...drawn.values()].map(n=>hotspot(n.n,n.x,n.y,n.w,n.h,{label:n.title})).join('');
  }
  function crusherMachineScene(){
    const positions=new Map(),drawn=[],parts=s.nodes.filter(n=>n.role==='part'),decor=[];
    const put=(n,x,y,w=180,h=110)=>{if(!n)return;positions.set(n.id,{x,y,w,h});drawn.push({n,x,y,w,h});};
    const pick=(rx,...pos)=>put(parts.find(n=>rx.test(n.label)),...pos);
    if(s.kind==='crusher'){
      decor.push(`<path d="M386 169H825V510L718 604H473L386 510Z" class="ps-building-frame"/>`,text(610,14,'RING GRANULATOR · OPEN ASSEMBLY','ps-zone-label'));
      pick(/Housing and access$/,456,24,260,120);pick(/Rotor assembly$/,480,254,245,145);
      pick(/Screen cage and adjustment$/,502,443,210,108);pick(/Rotor bearings and seals$/,838,259,180,115);
      pick(/Drive assembly$/,68,265,260,115);pick(/Hydraulic opening system$/,80,506,190,115);pick(/Protection and monitoring$/,896,51,175,113);pick(/Isolated foundation$/,466,637,280,100);
      decor.push(`<path class="ps-shaft" d="M285 340H490M719 340H860"/>`,text(609,833,'Motor → scoop coupling → rotor · open the drive to follow its oil circuit','ps-caption'));
    }else{
      decor.push(text(600,30,'SECONDARY GRIZZLY · OVERSIZE AND UNDERSIZE','ps-zone-label'));
      pick(/Screen body and deck$/,408,220,390,220);pick(/Vibrating drive assembly$/,80,154,210,145);pick(/Springs and supports$/,424,541,340,115);
      decor.push(`<path class="ps-assembly-leader" d="M270 259L405 310M575 432V542"/>`);
      const out=s.nodes.filter(n=>n.role==='connected'&&['crusher','feeder'].includes(n.kind));out.forEach((n,i)=>put(n,902,205+i*257,180,110));
      for(const n of out){const self={x:410,y:222,w:385,h:210};positions.set(s.id,self);}
    }
    for(const n of s.nodes.filter(n=>n.role==='detail')){const parent=M.closestParents(p,n.id).find(id=>positions.has(id));if(parent)positions.set(n.id,positions.get(parent));}
    const used=new Set(drawn.map(x=>x.n.id));const extra=parts.filter(n=>!used.has(n.id));extra.forEach((n,i)=>put(n,65+i%5*225,900+Math.floor(i/5)*190,170,95));
    s.height=extra.length?960+Math.ceil(extra.length/5)*190:900;s.initialHeight=Math.min(s.height,980);
    return decor.join('')+edgeMarkup(s.edges.filter(a=>positions.get(a.canonical_subject)!==positions.get(a.canonical_object)),positions)+drawn.map(x=>hotspot(x.n,x.x,x.y,x.w,x.h)).join('');
  }
  function dustExtractionScene(){
    const parts=s.nodes.filter(n=>n.role==='part'),pos=new Map(),drawn=[],decor=[];
    const put=(n,x,y,w=170,h=95)=>{if(n){pos.set(n.id,{x,y,w,h});drawn.push({n,x,y,w,h});}};
    if(s.kind==='de-house'){
      decor.push(text(600,35,'CAPTURE → SEPARATE → FILTER → EXHAUST','ps-zone-label'));
      parts.filter(n=>n.kind==='de-stream').forEach((n,i)=>put(n,235+i*490,90,245,160));
      parts.filter(n=>!/de-stream/.test(n.kind)).forEach((n,i)=>put(n,95+(i%4)*285,450+Math.floor(i/4)*215,185,110));
      decor.push(text(600,370,'Each stream has four hoods · open a stream to follow air and collected dust','ps-caption'));
    }else{
      const groups=['duct','cyclone','filter','fan'];groups.forEach((k,i)=>put(parts.find(n=>n.kind===k),60+i*292,165,185,123));
      const used=new Set(drawn.map(x=>x.n.id));parts.filter(n=>!used.has(n.id)).forEach((n,i)=>put(n,75+i%5*225,492+Math.floor(i/5)*200,165,100));
      decor.push(text(600,65,'DUST-LADEN AIR THROUGH THE EXTRACTION STREAM','ps-zone-label'),text(600,429,'Pulse cleaning, hopper discharge and damper controls stay with their equipment','ps-caption'));
    }
    const boundary=s.nodes.filter(n=>n.role==='connected');
    const bottom=Math.max(720,...drawn.map(x=>x.y+x.h+145));
    if(boundary.length)decor.push(text(600,bottom-25,'CONNECTIONS OUTSIDE THIS ASSEMBLY','ps-zone-label'));
    boundary.forEach((n,i)=>put(n,75+i%5*225,bottom+Math.floor(i/5)*205,165,100));
    // Project exact descendant endpoints onto their visible assembly; never invent an edge.
    for(const x of drawn)for(const child of p.assembly(x.n.id))if(!pos.has(child.id))pos.set(child.id,pos.get(x.n.id));
    const edges=p.networks.filter(a=>pos.has(a.canonical_subject)&&pos.has(a.canonical_object)&&pos.get(a.canonical_subject)!==pos.get(a.canonical_object));
    s.height=Math.max(820,...drawn.map(x=>x.y+x.h+115));s.initialHeight=s.height;
    return decor.join('')+edgeMarkup(edges,pos)+drawn.map(x=>hotspot(x.n,x.x,x.y,x.w,x.h)).join('');
  }
  function sprayScene(){
    const nodes=s.nodes.filter(n=>n.role==='part'),applications=nodes.filter(n=>(p.classes.get(n.id)||[]).includes('spray_application_point'));
    if(!applications.length)return null;
    const connected=connectedSprayScene(applications);if(connected)return connected;
    const groups=[[],[],[]];
    for(const n of applications){
      const target=(p.outgoing.get(n.id)||[]).find(a=>a.predicate==='sprays_at'),dest=p.entities.get(target?.canonical_object);
      const role=(p.outgoing.get(n.id)||[]).find(a=>a.predicate==='equipment_role')?.value||'';
      const row=/receiving/i.test(role)?2:(p.classes.get(dest?.id)||[]).includes('belt_feeder')?1:0;
      groups[row].push({n,dest});
    }
    let body=text(600,35,'DUST CONTROL AT EACH COAL TRANSFER','ps-zone-label');
    let visibleRows=0;
    groups.forEach((group,row)=>{
      if(!group.length)return;
      const y=90+(visibleRows++)*205;
      body+=text(45,y,['INCOMING CONVEYOR DISCHARGES','BELT-FEEDER DISCHARGES','RECEIVING CHUTES'][row],'ps-zone-label','start')+`<path d="M45 ${y+15}H1150" class="ps-floor"/>`;
      group.sort((a,b)=>a.n.label.localeCompare(b.n.label)).forEach(({n,dest},i)=>{
        const x=600-(group.length*230)/2+i*230+25;
        body+=hotspot(n,x,y+38,165,90,{label:n.label.replace(/^UEE-\d+ /,'')+(dest?' · '+dest.label:'')});
      });
    });
    const other=s.nodes.filter(n=>n.role!=='self'&&!applications.includes(n));
    const controlsY=95+visibleRows*205;
    body+=text(45,controlsY,'LOCAL CONTROLS & SHARED SUPPLY','ps-zone-label','start');
    other.forEach((n,i)=>body+=hotspot(n,65+(i%5)*230,controlsY+32+Math.floor(i/5)*195,165,95));
    s.height=controlsY+240+Math.max(0,Math.ceil(other.length/5)-1)*195;s.initialHeight=s.height;return body;
  }
  function connectedSprayScene(applications){
    const utilities=p.networks.filter(a=>a.context?.network==='utility');
    const chains=applications.map(ap=>{
      const descendants=new Set(p.assembly(ap.id).map(e=>e.id));
      const pru=utilities.find(a=>descendants.has(a.canonical_object)&&!descendants.has(a.canonical_subject))?.canonical_subject;
      const fas=utilities.find(a=>a.canonical_object===pru)?.canonical_subject;
      const dest=(p.outgoing.get(ap.id)||[]).find(a=>a.predicate==='sprays_at')?.canonical_object;
      return {ap,pru,fas,dest};
    });
    if(chains.some(c=>!c.pru||!c.fas))return null;
    chains.sort((a,b)=>a.ap.label.localeCompare(b.ap.label));
    const narrow=window.matchMedia('(max-width:760px)').matches,pos=new Map(),drawn=new Map(),byId=new Map(s.nodes.map(n=>[n.id,n]));
    const put=(id,x,y,w=165,h=95,title)=>{if(!p.entities.has(id))return;const n=byId.get(id)||{id,label:p.entities.get(id).label,kind:M.kind(p,id),role:'connected'};pos.set(id,{x,y,w,h});drawn.set(id,{n,x,y,w,h,title});};
    const branchIds=new Set(chains.flatMap(c=>[c.ap.id,c.pru,c.fas,c.dest]));
    const supply=s.nodes.filter(n=>n.role!=='self'&&!branchIds.has(n.id));
    supply.forEach((n,i)=>put(n.id,50+i%(narrow?2:5)*230,65+Math.floor(i/(narrow?2:5))*180));
    const start=125+Math.ceil(supply.length/(narrow?2:5))*180;
    const decor=[text(narrow?280:600,30,'LOCAL SUPPLY, CONTROLS & SHARED BOUNDARIES','ps-zone-label')];
    chains.forEach((c,i)=>{
      const y=start+i*(narrow?350:180);
      put(c.fas,50,y,165,95);put(c.pru,narrow?300:310,y,165,95);
      const count=(p.outgoing.get(c.ap.id)||[]).find(a=>a.predicate==='scheduled_nozzle_count')?.value||p.assembly(c.ap.id).flatMap(e=>p.outgoing.get(e.id)||[]).find(a=>a.predicate==='quantity'&&a.unit==='nozzles')?.value;
      put(c.ap.id,narrow?175:580,narrow?y+175:y,185,95,short(c.ap)+(count!==undefined?' · '+count+' nozzles':''));
      decor.push(text(50,y-20,(p.outgoing.get(c.ap.id)||[]).find(a=>a.predicate==='equipment_role')?.value||short(c.ap),'ps-zone-label','start'));
    });
    const destinations=[...new Set(chains.map(c=>c.dest).filter(Boolean))];
    const bottom=start+chains.length*(narrow?350:180);
    destinations.forEach((id,i)=>put(id,narrow?50+i%2*230:950,narrow?bottom+100+Math.floor(i/2)*180:start+i*230,175,100));
    // Project only exact descendant endpoints; no number-based branch association.
    for(const d of drawn.values())if(d.n.role!=='connected')for(const child of p.assembly(d.n.id))if(!pos.has(child.id))pos.set(child.id,pos.get(d.n.id));
    const regulators=new Set(chains.map(c=>c.pru)),consumers=new Set(destinations);
    const localIds=new Set(p.assembly(s.id).map(e=>e.id));
    const edges=p.networks.filter(a=>['utility','control'].includes(a.context?.network)&&(localIds.has(a.canonical_subject)||localIds.has(a.canonical_object))&&pos.has(a.canonical_subject)&&pos.has(a.canonical_object)&&pos.get(a.canonical_subject)!==pos.get(a.canonical_object)&&!(regulators.has(a.canonical_subject)&&consumers.has(a.canonical_object)));
    // Spray destination relations retain their original fact IDs and supports.
    // Utility color is presentation only; contradictory older PRU-to-belt
    // summaries remain inspectable on each regulator rather than double-routing.
    edges.push(...chains.flatMap(c=>(p.outgoing.get(c.ap.id)||[]).filter(a=>a.predicate==='sprays_at'&&pos.has(a.canonical_object)).map(a=>({...a,context:{...a.context,network:'utility'}}))));
    decor.push(text(50,start-55,'FAS → PRU → APPLICATION · QUALIFIED DESIGN DESTINATIONS','ps-zone-label','start'));
    s.width=narrow?570:1200;s.height=Math.max(bottom+140,...[...drawn.values()].map(d=>d.y+d.h+100));s.initialHeight=narrow?820:950;
    return decor.join('')+edgeMarkup(edges,pos)+[...drawn.values()].map(d=>hotspot(d.n,d.x,d.y,d.w,d.h,{label:d.title})).join('');
  }
  function conveyorScene(){
    const narrow=window.matchMedia('(max-width:760px)').matches;
    const positions=new Map(),routes=new Map(),drawn=[],decor=[];
    const parts=s.nodes.filter(n=>n.role==='part'||n.role==='located');
    const outside=s.nodes.filter(n=>n.role==='connected');
    const self=s.nodes.find(n=>n.role==='self');
    const byId=new Map(s.nodes.map(n=>[n.id,n]));
    const put=(n,x,y,w=126,h=74,title)=>{if(!n||positions.has(n.id))return;positions.set(n.id,{x,y,w,h});drawn.push({n,x,y,w,h,title});};

    // Classify internal parts into clean architectural bands (matching Silo House & Crusher House)
    const isDrivePart=n=>['motor','coupling','gearbox','brake','drive'].includes(n.kind)||/pulley/i.test(n.label)&&/head|drive/i.test(n.label);
    const isTopInline=n=>['weigher','detector'].includes(n.kind);
    const isProtectionOrClean=n=>['sensor','protection','scraper','marker'].includes(n.kind)||/cleaner|scraper|pcs|bss|zss|protection/i.test(n.label);
    const isDischargeInterface=n=>!isProtectionOrClean(n)&&(['chute','gate','tripper','stacker','reclaimer'].includes(n.kind)||/tripper|ftr-/i.test(n.label));

    const topInline=parts.filter(isTopInline);
    const driveParts=parts.filter(n=>!topInline.includes(n)&&isDrivePart(n));
    const dischargeParts=parts.filter(n=>!topInline.includes(n)&&!driveParts.includes(n)&&isDischargeInterface(n));
    const protParts=parts.filter(n=>!topInline.includes(n)&&!driveParts.includes(n)&&!dischargeParts.includes(n)&&isProtectionOrClean(n));
    const loopParts=parts.filter(n=>!topInline.includes(n)&&!driveParts.includes(n)&&!dischargeParts.includes(n)&&!protParts.includes(n));

    // Order drive parts strictly along the mechanical power-transmission shaft:
    // motor -> fluid/scoop coupling -> gearbox -> low-speed coupling -> head drive pulley -> service brake
    const driveOrder=n=>{
      const l=n.label.toLowerCase();
      if(n.kind==='drive')return 0;
      if(n.kind==='motor')return 1;
      if(n.kind==='coupling'&&!/low.speed/i.test(l))return 2;
      if(n.kind==='gearbox')return 3;
      if(n.kind==='coupling'&&/low.speed/i.test(l))return 4;
      if(n.kind==='pulley')return 5;
      if(n.kind==='brake')return 6;
      return 7;
    };
    driveParts.sort((a,b)=>driveOrder(a)-driveOrder(b)||a.label.localeCompare(b.label));

    const ownSet=new Set([s.id,...parts.map(n=>n.id)]);
    const matEdges=s.edges.filter(a=>a.context?.network==='material');
    const isSubChuteOfVisible=n=>{
      if(n.kind!=='chute')return false;
      const parents=M.closestParents(p,n.id);
      return parents.some(pid=>byId.has(pid)&&pid!==s.id);
    };
    const inlets=[],outlets=[],services=[];
    for(const n of outside){
      const feedsUs=matEdges.some(a=>a.canonical_subject===n.id&&ownSet.has(a.canonical_object));
      const fedByUs=matEdges.some(a=>ownSet.has(a.canonical_subject)&&a.canonical_object===n.id);
      if(isSubChuteOfVisible(n)){
        services.push(n);
        continue;
      }
      if(feedsUs&&!fedByUs)inlets.push(n);
      else if(fedByUs)outlets.push(n);
      else services.push(n);
    }
    inlets.sort((a,b)=>a.label.localeCompare(b.label,undefined,{numeric:true}));
    outlets.sort((a,b)=>a.label.localeCompare(b.label,undefined,{numeric:true}));
    services.sort((a,b)=>a.label.localeCompare(b.label,undefined,{numeric:true}));

    // Align dischargeParts horizontally with the downstream outlets they feed so bottom arrows never cross!
    dischargeParts.sort((a,b)=>{
      const outA=outlets.findIndex(o=>matEdges.some(e=>e.canonical_subject===a.id&&e.canonical_object===o.id));
      const outB=outlets.findIndex(o=>matEdges.some(e=>e.canonical_subject===b.id&&e.canonical_object===o.id));
      if(outA!==-1&&outB!==-1&&outA!==outB)return outA-outB;
      return a.label.localeCompare(b.label,undefined,{numeric:true});
    });

    const frameX=narrow?20:185,frameW=narrow?520:725;
    const centerX=frameX+frameW/2;
    const rowH=165;

    // 1. Top Band: UPSTREAM / RECEIVING (above frame)
    let curY=42;
    if(inlets.length){
      decor.push(text(centerX,22,'RECEIVING FROM UPSTREAM EQUIPMENT','ps-zone-label'));
      const cols=Math.min(inlets.length,narrow?3:4);
      const spacing=168,boxW=132;
      inlets.forEach((n,i)=>{
        const r=Math.floor(i/cols),c=i%cols,rowCount=Math.min(cols,inlets.length-r*cols);
        const startX=centerX-(rowCount*spacing)/2+(spacing-boxW)/2;
        put(n,startX+c*spacing,curY+r*152,boxW,72);
      });
      curY+=Math.ceil(inlets.length/cols)*152+32;
    }else{
      curY=55;
    }

    const frameTop=curY;
    const bands=[];

    // 2. Band A inside frame: CONVEYOR & INLINE WEIGHER / DETECTOR
    const beltY=curY+36;
    bands.push([beltY-12,'CONVEYOR']);
    if(topInline.length===0){
      put(self,centerX-130,beltY,260,86);
    }else if(topInline.length===1){
      put(topInline[0],centerX-220,beltY,150,82);
      put(self,centerX-30,beltY,250,86);
    }else{
      put(topInline[0],frameX+30,beltY,145,82);
      put(self,centerX-115,beltY,230,86);
      put(topInline[1],frameX+frameW-175,beltY,145,82);
    }
    curY=beltY+160;

    // 3. Band B inside frame: HEAD DRIVE TRAIN (left-to-right shaft order)
    if(driveParts.length){
      bands.push([curY,'HEAD DRIVE']);
      const rowY=curY+22;
      const mainChain=driveParts.filter(n=>n.kind!=='brake');
      const brakes=driveParts.filter(n=>n.kind==='brake');
      const cols=Math.min(mainChain.length,narrow?3:5);
      const spacing=narrow?165:140,boxW=narrow?135:114;
      mainChain.forEach((n,i)=>{
        const r=Math.floor(i/cols),c=i%cols,rowCount=Math.min(cols,mainChain.length-r*cols);
        const startX=centerX-(rowCount*spacing)/2+(spacing-boxW)/2;
        put(n,startX+c*spacing,rowY+r*rowH,boxW,72);
      });
      const chainRows=Math.max(1,Math.ceil(mainChain.length/cols));
      if(brakes.length){
        if(mainChain.length+brakes.length<=cols&&!narrow){
          const lastPos=mainChain.length?positions.get(mainChain[mainChain.length-1].id):{x:centerX-60};
          brakes.forEach((n,i)=>put(n,lastPos.x+spacing+i*spacing,rowY,boxW,72));
        }else{
          loopParts.unshift(...brakes);
        }
      }
      curY=rowY+chainRows*rowH;
    }

    // 4. Band C inside frame: BELT LOOP, PULLEYS, TAKE-UP & PROTECTION
    const mechAndProt=[...loopParts,...protParts];
    if(mechAndProt.length){
      bands.push([curY,'BELT & SUPPORT']);
      const rowY=curY+22;
      const cols=narrow?3:(mechAndProt.length===6?3:4);
      const spacing=narrow?168:175,boxW=narrow?138:138;
      mechAndProt.forEach((n,i)=>{
        const r=Math.floor(i/cols),c=i%cols,rowCount=Math.min(cols,mechAndProt.length-r*cols);
        const startX=centerX-(rowCount*spacing)/2+(spacing-boxW)/2;
        put(n,startX+c*spacing,rowY+r*rowH,boxW,74);
      });
      curY=rowY+Math.ceil(mechAndProt.length/cols)*rowH;
    }

    // 5. Band D inside frame: DISCHARGE CHUTES & FIXED TRIPPERS
    if(dischargeParts.length){
      bands.push([curY,'DISCHARGE & TRIPPER']);
      const rowY=curY+22;
      const cols=Math.min(dischargeParts.length,narrow?3:4);
      const spacing=narrow?168:175,boxW=narrow?138:140;
      dischargeParts.forEach((n,i)=>{
        const r=Math.floor(i/cols),c=i%cols,rowCount=Math.min(cols,dischargeParts.length-r*cols);
        const startX=centerX-(rowCount*spacing)/2+(spacing-boxW)/2;
        put(n,startX+c*spacing,rowY+r*rowH,boxW,74);
      });
      curY=rowY+Math.ceil(dischargeParts.length/cols)*rowH;
    }

    const frameH=Math.max(240,curY-frameTop+8);
    decor.unshift(`<rect x="${frameX}" y="${frameTop}" width="${frameW}" height="${frameH}" rx="10" class="ps-building-frame"/>`,
      text(frameX+20,frameTop+22,s.title.toUpperCase()+' · CONVEYOR & DRIVE ASSEMBLY','ps-zone-label','start'));
    for(const [y,label] of bands.slice(1)){
      decor.push(`<path d="M${frameX+14} ${y}H${frameX+frameW-14}" class="ps-floor"/>`);
      if(!narrow)decor.push(text(frameX-14,y+55,label,'ps-zone-label','end'));
    }
    if(!narrow&&bands.length)decor.push(text(frameX-14,bands[0][0]+52,bands[0][1],'ps-zone-label','end'));

    // 6. Bottom Band below frame: DOWNSTREAM / DISCHARGE RECEIVERS
    let bottomY=frameTop+frameH+54;
    if(outlets.length){
      decor.push(text(centerX,bottomY-18,'DISCHARGE TO DOWNSTREAM ROUTE','ps-zone-label'));
      const cols=Math.min(outlets.length,narrow?3:4);
      const spacing=175,boxW=140;
      outlets.forEach((n,i)=>{
        const r=Math.floor(i/cols),c=i%cols,rowCount=Math.min(cols,outlets.length-r*cols);
        const startX=centerX-(rowCount*spacing)/2+(spacing-boxW)/2;
        put(n,startX+c*spacing,bottomY+r*155,boxW,74);
      });
      bottomY+=Math.ceil(outlets.length/cols)*155+25;
    }

    // 7. Right-Hand Sidebar: SHARED SERVICES, SPRAY HEADERS & CONTROLS
    if(services.length){
      if(!narrow){
        const sideX=940,sideCols=services.length>5?2:1;
        decor.push(text(sideX+(sideCols===2?140:70),frameTop+10,'SHARED SERVICES & INTERFACES','ps-zone-label'));
        services.forEach((n,i)=>{
          const c=i%sideCols,r=Math.floor(i/sideCols);
          put(n,sideX+c*150,frameTop+30+r*155,130,72);
        });
      }else{
        decor.push(text(centerX,bottomY+15,'SHARED SERVICES & INTERFACES','ps-zone-label'));
        services.forEach((n,i)=>put(n,30+(i%3)*175,bottomY+35+Math.floor(i/3)*155,145,74));
        bottomY+=45+Math.ceil(services.length/3)*155;
      }
    }

    const sidebarSet=new Set(services.map(n=>n.id));
    const inletSet=new Set(inlets.map(n=>n.id));
    const outletSet=new Set(outlets.map(n=>n.id));
    const dischargeSet=new Set(dischargeParts.map(n=>n.id));
    const driveSet=new Set(driveParts.map(n=>n.id));

    const cleanEdges=s.edges.filter(a=>{
      const u=a.canonical_subject,v=a.canonical_object;
      if(!positions.has(u)||!positions.has(v)||positions.get(u)===positions.get(v))return false;
      if(sidebarSet.has(u)||sidebarSet.has(v))return false;
      if(a.context?.network==='mechanical'){
        return driveSet.has(u)&&driveSet.has(v)&&Math.abs(positions.get(u).y-positions.get(v).y)<30;
      }
      if(a.context?.network==='material'){
        if(inletSet.has(u)&&(v===s.id||topInline.some(x=>x.id===v)))return true;
        if(dischargeSet.has(u)&&outletSet.has(v))return true;
        if(u===s.id&&outletSet.has(v)&&!dischargeParts.length)return true;
        return false;
      }
      return false;
    });

    for(const a of cleanEdges){
      const f=positions.get(a.canonical_subject),t=positions.get(a.canonical_object);
      const k=a.canonical_subject+'>'+a.canonical_object;
      if(Math.abs(f.y-t.y)<25&&t.x>f.x){
        const y=f.y+f.h/2;
        routes.set(k,`M${f.x+f.w} ${y}L${t.x} ${y}`);
      }else if(a.canonical_subject===s.id&&outletSet.has(a.canonical_object)&&!dischargeParts.length){
        // Route from the bottom edge of the assembly frame so the arrow never cuts through HEAD DRIVE or BELT & SUPPORT!
        const x1=centerX,y1=frameTop+frameH,x2=t.x+t.w/2,y2=t.y-6;
        routes.set(k,`M${x1} ${y1}C${x1} ${(y1+y2)/2} ${x2} ${(y1+y2)/2} ${x2} ${y2}`);
      }else if(t.y>f.y){
        const x1=f.x+f.w/2,y1=f.y+f.h+42,x2=t.x+t.w/2,y2=t.y-6;
        routes.set(k,`M${x1} ${y1}C${x1} ${(y1+y2)/2} ${x2} ${(y1+y2)/2} ${x2} ${y2}`);
      }
    }

    const sideBottom=services.length&&!narrow?frameTop+50+Math.ceil(services.length/(services.length>5?2:1))*155:0;
    s.width=narrow?570:(services.length>5?1250:1200);
    s.height=Math.max(780,bottomY+45,sideBottom+45);
    s.initialHeight=Math.min(s.height,920);
    return decor.join('')+edgeMarkup(cleanEdges,positions,routes)+drawn.map(d=>hotspot(d.n,d.x,d.y,d.w,d.h,{label:d.title,max:d.w<=132?18:24})).join('');
  }
  function equipmentScene(){
    if(s.kind==='transfer'&&M.fixedTripperColumns(p,s.id).length)return fixedTripperScene();
    if(s.kind==='transfer'&&M.transferColumns(p,s.id).length)return transferHouseScene();
    if(s.kind==='conveyor'||s.kind==='feeder')return conveyorScene();
    if(s.kind==='crusher-house')return crusherHouseScene();
    // The secondary-screen layout expects the accepted crusher-package assemblies.
    // Other screen families use the general assembly view rather than an empty
    // secondary-screen frame with their parts pushed below it.
    if((s.kind==='crusher'||s.kind==='screen'&&s.nodes.some(n=>/Screen body and deck$/.test(n.label)))&&s.nodes.some(n=>n.role==='part'))return crusherMachineScene();
    if(['de-house','de-stream'].includes(s.kind))return dustExtractionScene();
    if(['silo-house','extractor'].includes(s.kind)||s.kind==='silo'&&(p.classes.get(s.id)||[]).includes('coal_silo'))return siloScene();
    if(s.kind==='spray-system'){const drawing=sprayScene();if(drawing)return drawing;}
    const parts=s.nodes.filter(n=>n.role==='part'||n.role==='located'),outside=s.nodes.filter(n=>n.role==='connected'),self=s.nodes.find(n=>n.role==='self');
    const positions=new Map(),decor=[],special=['yard','pile','conveyor','transfer','stacker','reclaimer','drive','mechanical','coupling'];
    let nodes=[];
    function place(n,x,y,w=150,height=100){if(!n)return;positions.set(n.id,{x,y,w,h:height});nodes.push({n,x,y,w,height});}
    if(s.kind==='yard'){
      const slots={pile:[490,300,250,168],shed:[450,35,330,180],stacker:[255,165,205,135],reclaimer:[830,245,205,137],conveyor:[65,290,200,130],water:[80,35,170,112],tank:[950,50,150,100],building:[180,515,130,86],pump:[950,510,150,100],assembly:[995,520,150,95]};
      const used={};for(const n of parts){let k=n.kind;const i=used[k]||0;used[k]=i+1;let pos=slots[k];if(k==='conveyor'&&i)pos=[770,490,240,125];else if(k==='building'&&i)pos=[400,535,130,86];else if(pos&&i)pos=null;place(n,...(pos||[35+(nodes.length%5)*225,720+Math.floor(nodes.length/5)*170,150,95]));}
      if(q().get('spread')!=='1'){
        const shed=nodes.find(x=>x.n.kind==='shed'),pile=nodes.find(x=>x.n.kind==='pile');
        if(shed&&pile){shed.x=390;shed.y=170;shed.w=440;shed.height=295;positions.set(shed.n.id,{x:shed.x,y:shed.y,w:shed.w,h:shed.height});nodes=nodes.filter(x=>x!==shed);nodes.unshift(shed);}
      }
      decor.push(`<path class="ps-yard-ground" d="M265 283L793 246L1055 439L558 522Z"/><path d="M262 432L899 426M280 445L915 439" class="ps-rail"/>${text(585,605,'STACKING · STORAGE · RECLAIMING','ps-zone-label')}`);
    }else if(s.kind==='drive'){
      const order=n=>/low.speed/i.test(n.label)?3:({motor:0,coupling:1,gearbox:2,pulley:4,bearing:4,'crusher-rotor':4,brake:5}[n.kind]??6),sorted=[...parts,...outside.filter(n=>['pulley','bearing','crusher-rotor'].includes(n.kind))].sort((a,b)=>order(a)-order(b));
      let i=0;sorted.forEach(n=>{if(n.kind==='brake')place(n,750,465,165,120);else{place(n,55+(i%5)*230,230+Math.floor(i/5)*245,165,120);i++;}});
      decor.push(text(600,145,'OPEN DRIVE ASSEMBLY','ps-zone-label'),text(600,178,'Follow the shaft connections. Open a component to see its auxiliaries.','ps-caption'));
    }else if(s.kind==='mechanical'){
      if(self)place(self,285,245,620,270);
      const spread=q().get('spread')==='1';
      const anchors=spread?[[860,95],[100,85],[525,65],[925,440],[165,480],[655,505]]:[[790,200],[135,460],[360,80],[920,415],[80,245],[655,505]];
      const sorted=[...parts].sort((a,b)=>Number(b.kind==='drive')-Number(a.kind==='drive'));
      sorted.forEach((n,i)=>place(n,...(anchors[i]||[70+(i%5)*220,750+Math.floor((i-6)/5)*180]),160,100));
      decor.push(`<path class="ps-floor" d="M240 507H947"/>${text(610,666,'Select an assembly to open its connected parts','ps-caption')}`);
    }else if(s.kind==='transfer'){
      decor.push(`<path class="ps-building-frame" d="M310 625V115L600 42L890 115V625M310 115H890M310 315H890M310 575H890M340 120V570M862 120V570"/>${text(600,101,'TRANSFER HOUSE · CUTAWAY','ps-zone-label')}`);
      const used={};parts.forEach((n,i)=>{const k=n.kind,j=used[k]||0;used[k]=j+1;const isB=/\b\d+B\b/.test(n.label);let pos;
        if(k==='chute')pos=[isB?655:355,/receiving/i.test(n.label)?390:205,130,92];
        else if(k==='drive')pos=[isB?900:120,190,155,110];
        else if(k==='water')pos=[38,415,170,110];
        else if(k==='tank')pos=[930,55,140,95];
        else if(k==='pump')pos=[925,510,145,95];
        else pos=[70+(i%5)*225,735+Math.floor(i/5)*170,145,92];place(n,...pos);});
    }else if(s.kind==='pile'){
      if(self)place(self,405,210,390,230);
      const places={stacker:[120,160,210,140],reclaimer:[865,230,220,145],shed:[440,10,325,165]},used={};let water=0,extra=0;
      [...parts,...outside].forEach(n=>{const count=used[n.kind]||0;used[n.kind]=count+1;const pos=n.kind==='water'?[85+(water++%3)*350,520+Math.floor((water-1)/3)*200,170,112]:!count&&places[n.kind]?places[n.kind]:[60+(extra++%5)*230,760+Math.floor((extra-1)/5)*200,160,110];place(n,...pos);});
    }else if(s.kind==='coupling'&&parts.some(n=>n.kind==='pump')){
      if(self)place(self,490,150,280,185);
      let extra=0,filterIndex=0;parts.forEach(n=>{const t=n.label.toLowerCase();let pos;
        if(n.kind==='pump')pos=[570,455,165,112];
        else if(n.kind==='cooler')pos=[775,455,165,112];
        else if(n.kind==='tank')pos=[40,455,175,112];
        else if(/strainer/.test(t))pos=[245,455,145,112];
        else if(n.kind==='valve')pos=[405,455,135,112];
        else if(n.kind==='filter')pos=[945,120+(filterIndex++)*280,165,112];
        else if(/actuator/.test(t))pos=[130,150,175,112];
        else{pos=[55+(extra%5)*230,815+Math.floor(extra/5)*200,160,105];extra++;}place(n,...pos);});
      decor.push(text(600,705,'OIL CIRCULATION · arrows follow the documented P&I connections','ps-caption'),text(45,785,'PROTECTION & INSTRUMENTATION · PAN DOWN OR CHOOSE ALL PARTS','ps-zone-label','start'));
    }else if(s.kind==='pump'&&parts.some(n=>/shaft and sleeves/i.test(n.label))&&parts.some(n=>/impeller/i.test(n.label))){
      const anchors=[[/ Motor$/,[520,45]], [/Flexible coupling$/,[525,230]], [/Thrust stand$/,[520,415]], [/Shaft and sleeves$/,[525,605]], [/impeller$/,[525,795]], [/Suction strainer$/,[525,980]], [/casing$/,[860,795]], [/Gland packing$/,[860,415]], [/rubber bushes$/,[160,605]], [/Self-water lubrication line$/,[160,795]]];
      let extra=0;for(const n of parts){const a=anchors.find(([pattern])=>pattern.test(n.label));place(n,...(a?a[1]:[55+(extra++%5)*230,1200]),170,110);}
      decor.push(text(600,25,'VERTICAL PUMP · MOTOR TO IMPELLER','ps-zone-label'),`<path d="M610 180V1055" class="ps-shaft"/>`,text(180,500,'LUBRICATION & COLUMN SUPPORT','ps-zone-label'));
    }else if(['stacker','reclaimer'].includes(s.kind)){
      // Structured machine house frame for Stackers & Reclaimers
      decor.push(`<rect x="190" y="155" width="680" height="460" rx="10" class="ps-building-frame"/>`,
        text(210,178,s.title.toUpperCase()+' · MACHINE SUB-ASSEMBLIES','ps-zone-label','start'));
      if(self)place(self,410,20,240,115);
      parts.forEach((n,i)=>{
        const r=Math.floor(i/3),c=i%3;
        place(n,225+c*215,205+r*135,175,92);
      });
    }else if(['silo','crusher','screen','ship','building','shed'].includes(s.kind)){
      if(self)place(self,405,215,390,230);
      const anchors=[[70,75],[485,20],[935,85],[55,345],[930,345],[130,570],[490,585],[870,570]];
      parts.forEach((n,i)=>place(n,...(anchors[i]||[45+(i%5)*235,810+Math.floor((i-8)/5)*175]),160,105));
    }else{
      if(self)place(self,465,55,270,160);
      parts.forEach((n,i)=>place(n,65+(i%5)*230,365+Math.floor(i/5)*220,165,110));
    }
    if(!parts.length&&!self&&s.kind!=='missing')return '';
    // External assets remain outside the assembly, even when they serve it.
    const boundaryNodes=outside.filter(n=>!positions.has(n.id));
    let maxY=Math.max(720,...nodes.map(n=>n.y+n.height+105));
    const parentPos=self?positions.get(self.id):null;
    let leaders='';
    if(parentPos&&!['stacker','reclaimer'].includes(s.kind))for(const item of nodes.filter(n=>n.n.role==='part'||n.n.role==='located')){
      const from={x:parentPos.x+parentPos.w/2,y:parentPos.y+parentPos.h/2},to={x:item.x+item.w/2,y:item.y+item.height/2};
      leaders+=`<path class="ps-assembly-leader ${item.n.role==='located'?'ps-location-leader':''}" d="M${from.x} ${from.y}L${to.x} ${to.y}"/>`;
    }
    boundaryNodes.forEach((n,i)=>place(n,55+(i%5)*230,maxY+45+Math.floor(i/5)*205,165,100));
    if(boundaryNodes.length)decor.push(text(600,maxY+10,'CONNECTED EQUIPMENT & SHARED SERVICES','ps-zone-label'));
    const boundarySet=new Set(boundaryNodes.map(n=>n.id));
    const drawnEdges=s.edges.filter(a=>!(boundarySet.has(a.canonical_subject)&&a.canonical_object===s.id&&a.context?.network==='utility'));
    s.height=Math.max(maxY,...nodes.map(n=>n.y+n.height+105));s.initialHeight=720;
    return decor.join('')+leaders+edgeMarkup(drawnEdges,positions)+nodes.map(({n,x,y,w,height})=>hotspot(n,x,y,w,height)).join('');
  }
  function transferSelection(){
    const columns=M.transferColumns(p,s.id),index=Math.max(0,Math.min(columns.length-1,Number(q().get('transferstream'))||0)),column=columns[index];
    return {columns,index,column,outlet:column?.outlets.includes(q().get('transferoutlet'))?q().get('transferoutlet'):column?.outlets[0]};
  }
  function transferRouteGuide(){
    const fixed=M.fixedTripperColumns(p,s.id);
    if(fixed.length&&q().get('scene')!=='connections')return `<div class="ps-crusher-guide"><nav aria-label="Fixed-tripper branch">${[['through','Same-belt continuation'],['yard','Yard diversion']].map(([key,name])=>`<a href="${safe(url({fixedmode:key,pick:null,edge:null}))}" ${(q().get('fixedmode')||'through')===key?'aria-current="true"':''}>${name}</a>`).join('')}</nav><small>Fixed trippers divert coal to the yard or pass it onward on the same continuous belt. The two views of each belt show its entry and continuation, not a return loop. Illustrative selection; partial splitting remains a documented alternative.</small>${fixed.map(c=>`<p>${safe(p.entities.get(c.inlet).label)} → ${safe(p.entities.get(c.tripper).label)} → ${safe(p.entities.get(c.gate).label)}${c.edges.filter(a=>a.canonical_subject===c.gate).map(a=>`<br>${safe(p.entities.get(a.canonical_object).label)}: ${safe(a.context?.condition||'Source-drawn branch')} ${source(a,'Route source ↗')}`).join('')}</p>`).join('')}</div>`;
    if(s.kind!=='transfer'||!M.transferColumns(p,s.id).length||q().get('scene')==='connections')return '';
    const v=transferSelection(),group=(title,items,key,sel)=>`<div><span>${title}</span><nav aria-label="${title}">${items.map(([id,name])=>`<a href="${safe(url({[key]:id,pick:null,edge:null}))}" ${String(id)===String(sel)?'aria-current="true"':''}>${safe(name)}</a>`).join('')}</nav></div>`;
    const selected=M.transferRoute(p,v.column,v.outlet).filter(a=>v.column?.gates.includes(a.canonical_subject));
    const locations=(p.outgoing.get(s.id)||[]).filter(a=>a.predicate==='location_description'&&typeof a.value==='string');
    return `<div class="ps-crusher-guide">${group('Follow incoming conveyor',v.columns.map((c,i)=>[i,c.inlets.map(id=>p.entities.get(id).label).join(' / ')]),'transferstream',v.index)}${group('Selected receiving conveyor',(v.column?.outlets||[]).map(id=>[id,p.entities.get(id).label]),'transferoutlet',v.outlet)}<small>${safe(selected.map(a=>a.context?.condition||'').filter(Boolean).join(' · '))} · illustrative selection, no live status</small>${locations.map(a=>`<p class="ps-transfer-location">${safe(a.value)} ${source(a,'Location source ↗')}</p>`).join('')}</div>`;
  }
  function transferHouseScene(){
    const v=transferSelection(),positions=new Map(),drawn=new Map(),byId=new Map(s.nodes.map(n=>[n.id,n]));
    const narrow=window.matchMedia('(max-width:760px)').matches;
    const put=(id,x,y,w=160,h=90,title)=>{const n=byId.get(id);if(n){positions.set(id,{x,y,w,h});drawn.set(id,{n,x,y,w,h,title});}};
    const colCount=Math.max(2,v.columns.length);
    const colStep=colCount>2?Math.min(260,Math.floor(720/colCount)):340;
    const frameW=Math.max(640,colCount*colStep+80);
    const laneParts=new Set(),decor=[`<rect x="245" y="180" width="${frameW}" height="620" rx="8" class="ps-building-frame"/>`,text(245+frameW/2,24,'INCOMING CONVEYORS · OPEN TO EXPLORE THEIR PARTS','ps-zone-label')];
    v.columns.forEach((c,i)=>{
      const located=s.nodes.filter(n=>n.role==='located'&&M.closestParents(p,n.id).some(id=>c.inlets.includes(id)));
      const drive=located.find(n=>n.kind==='drive'),chutes=located.filter(n=>n.kind==='chute');
      c.gates.forEach(id=>laneParts.add(id));if(drive)laneParts.add(drive.id);chutes.forEach(n=>laneParts.add(n.id));
      if(narrow&&i!==v.index)return;
      const x=narrow?50:305+i*colStep;c.inlets.forEach((id,j)=>put(id,x+j*175,58,Math.min(180,colStep-25),95));put(c.gate,x+15,425,135,83);
      c.gates.filter(id=>id!==c.gate).forEach((id,j)=>put(id,x+15+j*145,545,135,83));
      if(drive)put(drive.id,narrow?325:x-125,narrow?65:225,130,70,'Head drive · '+c.inlets.map(id=>p.entities.get(id).label).join(' / '));
      chutes.forEach((n,j)=>put(n.id,x+15+j*145,230,135,65,'Discharge chute · '+c.inlets.map(id=>p.entities.get(id).label).join(' / ')));
    });
    const outlets=narrow?[v.outlet]:[...new Set(v.columns.flatMap(c=>c.outlets))];
    const outStep=outlets.length>2?Math.floor((frameW-80)/outlets.length):340;
    outlets.forEach((id,i)=>put(id,narrow?50:300+i*outStep,665,Math.min(180,outStep-20),88));
    decor.push(`<path d="M263 410H${245+frameW-18}M263 640H${245+frameW-18}" class="ps-floor"/>`,text(220,469,'DIVERT','ps-zone-label','end'),text(220,710,'RECEIVE','ps-zone-label','end'));
    const services=s.nodes.filter(n=>n.role==='part'&&!drawn.has(n.id));
    const svcX=narrow?325:(245+frameW+55);
    services.forEach((n,i)=>{
      const applications=p.assembly(n.id).filter(e=>(p.classes.get(e.id)||[]).includes('spray_application_point')).length;
      const title=applications?`DFDS · ${applications} application points`:/Sump Pumps/.test(n.label)?'Drainage · '+short(n):/Service and drinking/.test(n.label)?'Service & drinking water':short(n);
      put(n.id,svcX,(narrow?255:70)+i*187,175,90,title);
    });
    const active=M.transferRoute(p,v.column,v.outlet),keys=new Set(active.map(a=>a.canonical_subject+'>'+a.canonical_object));
    const relevant=[...new Set(v.columns.flatMap(c=>c.outlets.flatMap(outlet=>M.transferRoute(p,c,outlet))))].filter(a=>positions.has(a.canonical_subject)&&positions.has(a.canonical_object));
    const routes=new Map(relevant.map(a=>{const f=positions.get(a.canonical_subject),t=positions.get(a.canonical_object);return [a.canonical_subject+'>'+a.canonical_object,`M${f.x+f.w/2} ${f.y+f.h}C${f.x+f.w/2} ${f.y+f.h+45} ${t.x+t.w/2} ${t.y-45} ${t.x+t.w/2} ${t.y}`];}));
    const other=s.nodes.filter(n=>!drawn.has(n.id)&&(n.role==='connected'||n.role==='located'&&!laneParts.has(n.id)));
    const bottom=Math.max(880,(narrow?280:95)+services.length*187);
    other.forEach((n,i)=>put(n.id,65+i%(narrow?2:5)*230,bottom+60+Math.floor(i/(narrow?2:5))*205,165,95));
    if(other.length)decor.push(text(600,bottom+25,'OTHER LOCATED EQUIPMENT & CONNECTIONS','ps-zone-label'));
    s.width=narrow?550:Math.max(1200,svcX+230);s.height=bottom+120+Math.ceil(other.length/(narrow?2:5))*205;s.initialHeight=870;
    if(narrow){decor.length=0;decor.push(`<rect x="25" y="180" width="225" height="620" rx="8" class="ps-building-frame"/>`,text(140,24,'SELECTED TRANSFER ROUTE','ps-zone-label'),`<path d="M40 410H235M40 640H235" class="ps-floor"/>`,text(275,bottom+25,'OTHER LOCATED EQUIPMENT & CONNECTIONS','ps-zone-label'));}
    return decor.join('')+`<g class="ps-route-inactive">${edgeMarkup(relevant.filter(a=>!keys.has(a.canonical_subject+'>'+a.canonical_object)),positions,routes)}</g>`+edgeMarkup(active,positions,routes)+[...drawn.values()].map(n=>hotspot(n.n,n.x,n.y,n.w,n.h,{label:n.title,max:n.w<=135?16:26})).join('');
  }
  function fixedTripperScene(){
    const columns=M.fixedTripperColumns(p,s.id),positions=new Map(),drawn=new Map(),byId=new Map(s.nodes.map(n=>[n.id,n]));
    const narrow=window.matchMedia('(max-width:760px)').matches,lanes=new Set(columns.flatMap(c=>[c.inlet,c.tripper,c.gate,...c.outlets]));
    const put=(id,x,y,w=165,h=90,title)=>{const n=byId.get(id);if(n){positions.set(id,{x,y,w,h});drawn.set(id,{n,x,y,w,h,title});}};
    const routes=new Map(),continuations=[],decor=[];
    if(!narrow)decor.push(`<rect x="65" y="15" width="1060" height="700" rx="10" class="ps-building-frame"/>`);
    columns.forEach((c,i)=>{
      const x=narrow?50:120+i*520,top=narrow?i*700:0;
      put(c.inlet,x,top+55,180,90);put(c.tripper,x,top+210);put(c.gate,x,top+365);
      continuations.push(hotspot(byId.get(c.inlet),x,top+535,180,90,{label:p.entities.get(c.inlet).label+' continues'}));
      decor.push(text(x+90,top+35,'SAME CONTINUOUS BELT','ps-zone-label'),text(x+90,top+685,'ONWARD TO NEXT TRANSFER','ps-caption'));
      c.outlets.filter(id=>id!==c.inlet).forEach((id,j)=>{put(id,x+235,top+530+j*140,180,90);continuations.push(hotspot(byId.get(id),x+235,top+530+j*140,180,90));drawn.delete(id);});
      c.edges.forEach(a=>{
        const f=positions.get(a.canonical_subject),t=a.canonical_object===c.inlet?{x,y:top+535,w:180}:positions.get(a.canonical_object);
        if(f&&t)routes.set(a.canonical_subject+'>'+a.canonical_object,`M${f.x+f.w/2} ${f.y+f.h}L${t.x+t.w/2} ${t.y}`);
      });
    });
    const base=narrow?columns.length*700:740,other=s.nodes.filter(n=>n.role!=='self'&&!lanes.has(n.id));
    other.forEach((n,i)=>put(n.id,50+i%(narrow?2:5)*225,base+85+Math.floor(i/(narrow?2:5))*185));
    decor.push(text(narrow?275:600,base+35,'LOCAL ASSEMBLIES & SHARED SERVICES','ps-zone-label'));
    s.width=narrow?550:1200;s.height=base+170+Math.ceil(other.length/(narrow?2:5))*185;s.initialHeight=narrow?740:900;
    const selected=[],inactive=[],yard=q().get('fixedmode')==='yard';
    columns.forEach(c=>c.edges.forEach(a=>(a.canonical_subject!==c.gate||(a.canonical_object!==c.inlet)===yard?selected:inactive).push(a)));
    return decor.join('')+`<g class="ps-route-inactive">${edgeMarkup(inactive,positions,routes)}</g>`+edgeMarkup(selected,positions,routes)+[...drawn.values()].map(n=>hotspot(n.n,n.x,n.y,n.w,n.h,{label:n.title})).join('')+continuations.join('');
  }
  function measuredConveyorScene(){
    return conveyorScene();
  }
  function connectionsScene(){
    const positions=new Map(),self=s.nodes.find(n=>n.id===s.id),edges=s.edges,layer=q().get('layer')||'all';
    const visible=edges.filter(a=>layer==='all'||a.context.network===layer),ids=new Set(visible.flatMap(a=>[a.canonical_subject,a.canonical_object]));
    const ins=s.nodes.filter(n=>n.id!==s.id&&visible.some(a=>a.canonical_subject===n.id&&a.canonical_object===s.id));
    const outs=s.nodes.filter(n=>n.id!==s.id&&!ins.includes(n)&&visible.some(a=>a.canonical_subject===s.id&&a.canonical_object===n.id));
    const others=s.nodes.filter(n=>n.id!==s.id&&!ins.includes(n)&&!outs.includes(n)&&ids.has(n.id));
    const rows=Math.max(ins.length,outs.length,1),base=Math.max(460,rows*170+75);
    if(self)positions.set(self.id,{x:475,y:Math.min(base/2,300)-40,w:250,h:165});
    ins.forEach((n,i)=>positions.set(n.id,{x:75,y:70+i*170,w:175,h:105}));
    outs.forEach((n,i)=>positions.set(n.id,{x:950,y:70+i*170,w:175,h:105}));
    others.forEach((n,i)=>positions.set(n.id,{x:65+(i%5)*230,y:base+100+Math.floor(i/5)*210,w:170,h:108}));
    s.height=Math.max(720,base+Math.ceil(others.length/5)*210+130);s.initialHeight=Math.min(s.height,950);
    return text(165,35,'SUPPLYING / UPSTREAM','ps-zone-label')+text(1040,35,'RECEIVING / DOWNSTREAM','ps-zone-label')+edgeMarkup(visible,positions)+s.nodes.filter(n=>positions.has(n.id)).map(n=>{const a=positions.get(n.id);return hotspot(n,a.x,a.y,a.w,a.h);}).join('')+(!visible.length?text(600,550,'No documented directed connections in this layer.','ps-caption'):'');
  }
  function contextRail(){
    if(!s.id)return '';
    const inside=new Set(['silo-house','crusher-house'].includes(s.kind)?p.assembly(s.id).map(n=>n.id):[s.id]);
    const edges=p.material.filter(a=>inside.has(a.canonical_subject)!==inside.has(a.canonical_object)),other=[...new Set(edges.map(a=>inside.has(a.canonical_subject)?a.canonical_object:a.canonical_subject))];
    return `<div class="ps-route-context"><span>In the plant</span>${other.slice(0,8).map(id=>{const incoming=edges.some(a=>a.canonical_subject===id&&inside.has(a.canonical_object));return `<a href="${safe(openURL(id))}">${incoming?'← from':'to →'} <strong>${safe(p.entities.get(id)?.label)}</strong></a>`;}).join('')}<a class="ps-context-more" href="${safe(url({scene:q().get('scene')==='connections'?null:'connections',pick:null,edge:null}))}">${q().get('scene')==='connections'?'↶ Back to assembly':'View connections ↗'}</a></div>`;
  }
  function structuredAreaScene(){
    const positions=new Map(),routes=new Map(),drawn=new Map(),decor=[];
    const members=new Map(s.nodes.map(n=>[n.id,n]));
    const byLabel=new Map(s.nodes.map(n=>[n.label.toUpperCase().trim(),n]));
    const put=(n,x,y,w=150,h=76,title)=>{if(!n||drawn.has(n.id))return;positions.set(n.id,{x,y,w,h});drawn.set(n.id,{n,x,y,w,h,title});};
    const putLabel=(lbl,x,y,w=150,h=76,title)=>{const n=byLabel.get(lbl.toUpperCase());if(n)put(n,x,y,w,h,title);};

    const chuteOwner=new Map();
    for(const n of s.nodes){
      if(n.kind==='chute'||(p.classes.get(n.id)||[]).includes('chute_interface')){
        const owner=M.closestParents(p,n.id).find(pid=>members.has(pid)&&pid!==n.id);
        if(owner)chuteOwner.set(n.id,owner);
      }
    }

    if(s.area==='distribution'){
      const frameX=190,frameY=55,frameW=735,frameH=1660;
      decor.push(`<rect x="${frameX}" y="${frameY}" width="${frameW}" height="${frameH}" rx="10" class="ps-building-frame"/>`,
        text(frameX+20,frameY+24,'UEF-3 → UEF-7 · TWIN-STREAM STACKING & SILO-FEED CORRIDOR','ps-zone-label','start'),
        text(555,28,'FROM PRIMARY SCREENHOUSE (EAC-3A / EAC-3B)','ps-zone-label'),
        text(1055,75,'TRANSFER HOUSES & ANALYSERS','ps-zone-label'));
      const bands=[
        [95,'UEF-3 · DIVIDERS',[['KB-FD-1',285],['KB-FD-2',615]]],
        [255,'UEF-3 · SELECTORS',[['FG-1',285],['FG-2',615]]],
        [415,'CONVEYORS 4A / 4B',[['EAC-4A',285],['EAC-4B',615]]],
        [575,'UEF-4 · TRIPPERS',[['FTR-1',210],['KB-FD-3',385],['FTR-2',570],['KB-FD-4',745]]],
        [735,'UEF-5 · DIVIDERS',[['KB-FD-5',285],['KB-FD-6',615]]],
        [895,'UEF-5 · SELECTORS',[['FG-3',285],['FG-4',615]]],
        [1055,'CONVEYORS 5A / 5B',[['EAC-5A',285],['EAC-5B',615]]],
        [1215,'UEF-6 · TRIPPERS',[['FTR-3',210],['KB-FD-7',385],['FTR-4',570],['KB-FD-8',745]]],
        [1375,'UEF-7 · SELECTORS',[['FG-5',285],['FG-6',615]]],
        [1535,'SILO-FEED BELTS',[['EBA-6A',285],['EBA-6B',615]]]
      ];
      bands.forEach(([y,title,items],idx)=>{
        if(idx>0)decor.push(`<path d="M${frameX+14} ${y-18}H${frameX+frameW-14}" class="ps-floor"/>`);
        decor.push(text(frameX-14,y+42,title,'ps-zone-label','end'));
        const w=items.length>2?132:165;
        items.forEach(([lbl,x])=>putLabel(lbl,x,y,w,74));
      });
      ['UEF-3','UEF-4','UEF-5','UEF-6','UEF-7','CV-1','CV-2'].forEach((lbl,i)=>putLabel(lbl,965,95+i*158,160,74));
      s.width=1200;s.height=1760;s.initialHeight=980;
    }else if(s.area==='reclaim'){
      const frameX=190,frameY=65,frameW=735,frameH=675;
      decor.push(`<rect x="${frameX}" y="${frameY}" width="${frameW}" height="${frameH}" rx="10" class="ps-building-frame"/>`,
        text(frameX+20,frameY+24,'UEF-8 TO UEF-12 · RECLAIM COLLECTION & SILO-FEED CORRIDOR','ps-zone-label','start'),
        text(555,34,'FROM STOCKYARD RECLAIM CONVEYORS (EBA-8 / 10 / 12 / 14)','ps-zone-label'),
        text(1070,85,'TRANSFER HOUSES & WEIGHERS','ps-zone-label'));
      const bands=[
        [110,'YARD RECLAIM GATES',[['FG-7',210],['FG-8',385],['FG-9',560],['FG-10',735]]],
        [275,'COLLECTOR BELTS',[['EBA-15A',290],['EBA-15B',610]]],
        [440,'UEF-12 · SELECTORS',[['FG-11',290],['FG-12',610]]],
        [605,'SILO-FEED BELTS',[['EBA-16A',290],['EBA-16B',610]]]
      ];
      bands.forEach(([y,title,items],idx)=>{
        if(idx>0)decor.push(`<path d="M${frameX+14} ${y-20}H${frameX+frameW-14}" class="ps-floor"/>`);
        decor.push(text(frameX-14,y+42,title,'ps-zone-label','end'));
        const w=items.length>2?135:170;
        items.forEach(([lbl,x])=>putLabel(lbl,x,y,w,74));
      });
      ['UEF-8','UEF-9','UEF-10','UEF-11','UEF-12','AT-3','AT-4','CV-3','CV-4'].forEach((lbl,i)=>{
        putLabel(lbl,955+(i%2)*148,105+Math.floor(i/2)*152,130,72);
      });
      s.width=1250;s.height=820;s.initialHeight=820;
    }else if(s.area==='unloading'){
      const frameX=190,frameY=65,frameW=735,frameH=675;
      decor.push(`<rect x="${frameX}" y="${frameY}" width="${frameW}" height="${frameH}" rx="10" class="ps-building-frame"/>`,
        text(frameX+20,frameY+24,'COAL JETTY · UNLOADING & WEIGHING CORRIDOR','ps-zone-label','start'),
        text(1070,85,'FACILITIES & DETECTORS','ps-zone-label'));
      const bands=[
        [110,'SHIP UNLOADERS',[['Coal Ship Unloader-1',220],['Coal Ship Unloader-2',470],['Coal Ship Unloader-3',720]]],
        [275,'JETTY CONVEYORS',[['EAC-1A',290],['EAC-1B',610]]],
        [440,'TRANSFER HOUSE',[['UEF-1',450]]],
        [605,'PLANT APPROACH',[['EAC-2A',290],['EAC-2B',610]]]
      ];
      bands.forEach(([y,title,items],idx)=>{
        if(idx>0)decor.push(`<path d="M${frameX+14} ${y-20}H${frameX+frameW-14}" class="ps-floor"/>`);
        decor.push(text(frameX-14,y+42,title,'ps-zone-label','end'));
        items.forEach(([lbl,x])=>putLabel(lbl,x,y,165,74));
      });
      ['Coal Jetty','AT-1','AT-2','EAT-1','EAT-2','QB-1','QB-2'].forEach((lbl,i)=>{
        putLabel(lbl,955+(i%2)*148,105+Math.floor(i/2)*152,130,72);
      });
      s.width=1250;s.height=820;s.initialHeight=820;
    }else if(s.area==='screening'){
      const frameX=190,frameY=65,frameW=735,frameH=675;
      decor.push(`<rect x="${frameX}" y="${frameY}" width="${frameW}" height="${frameH}" rx="10" class="ps-building-frame"/>`,
        text(frameX+20,frameY+24,'UEE-1 · PRIMARY SCREENHOUSE','ps-zone-label','start'),
        text(1055,85,'HOUSE & SAMPLING','ps-zone-label'));
      const bands=[
        [110,'ROD GATES',[['KB-RG-1',210],['KB-RG-2',385],['KB-RG-3',560],['KB-RG-4',735]]],
        [275,'BYPASS GATES',[['KB-RPG-1',210],['KB-RPG-2',385],['KB-RPG-3',560],['KB-RPG-4',735]]],
        [440,'PRIMARY SCREENS',[['EBD-1',210],['EBD-2',385],['EBD-3',560],['EBD-4',735]]],
        [605,'ONWARD CONVEYORS',[['EAC-3A',290],['EAC-3B',610]]]
      ];
      bands.forEach(([y,title,items],idx)=>{
        if(idx>0)decor.push(`<path d="M${frameX+14} ${y-20}H${frameX+frameW-14}" class="ps-floor"/>`);
        decor.push(text(frameX-14,y+42,title,'ps-zone-label','end'));
        const w=items.length>2?135:170;
        items.forEach(([lbl,x])=>putLabel(lbl,x,y,w,74));
      });
      ['UEE-1','UEE-1 Oversize Reject Bins','EAU-1','UEF-3 Coal Sampling System'].forEach((lbl,i)=>putLabel(lbl,960,105+i*155,165,76));
      s.width=1220;s.height=820;s.initialHeight=820;
    }else if(s.area==='stockyard'){
      const gateways=s.nodes.filter(n=>n.kind==='yard');
      const bodyGateways=gateways.map((n,i)=>`<a class="ps-area-gateway" href="${safe(openURL(n.id))}"><g transform="translate(${45+i*240} 15)"><rect class="ps-halo" x="-5" y="0" width="215" height="175" rx="18"/>${symbol('yard',15,0,165,110)}${text(100,132,n.label,'ps-stage-title')}${text(100,155,'Open yard assembly →','ps-node-hint')}</g></a>`).join('');
      const frameX=150,frameY=225,frameW=1035,frameH=670;
      decor.push(bodyGateways,`<rect x="${frameX}" y="${frameY}" width="${frameW}" height="${frameH}" rx="10" class="ps-building-frame"/>`,
        text(frameX+20,frameY+24,'COAL STOCKYARDS 1–4 · STACKING → STORAGE → RECLAIMING LANES','ps-zone-label','start'));
      for(let yIdx=0;yIdx<4;yIdx++){
        const n=yIdx+1,rowY=268+yIdx*156;
        if(yIdx>0)decor.push(`<path d="M${frameX+14} ${rowY-16}H${frameX+frameW-14}" class="ps-floor"/>`);
        decor.push(text(frameX-14,rowY+42,`YARD ${n}`,'ps-zone-label','end'));
        const rowItems=[[f=>`EAC-${5+2*f}`,175],[f=>`EAD-${f}`,380],[f=>`EAE-${f}`,585],[f=>`EAF-${f}`,790],[f=>`EBA-${6+2*f}`,995]];
        rowItems.forEach(([fn,x])=>putLabel(fn(n),x,rowY,150,74));
      }
      s.width=1220;s.height=940;s.initialHeight=940;
    }else if(s.area==='bunkers'){
      const frameX=155,frameY=55,frameW=1025,frameH=795;
      decor.push(`<rect x="${frameX}" y="${frameY}" width="${frameW}" height="${frameH}" rx="10" class="ps-building-frame"/>`,
        text(frameX+20,frameY+24,'UNIT-1 & UNIT-2 BOILER COAL BUNKER BAYS (TT-1–4 · BUNKERS A–F)','ps-zone-label','start'),
        `<path d="M668 ${frameY+40}V${frameY+frameH-15}" class="ps-floor"/>`);
      const bands=[
        [95,'TRIPPERS',[['TT-1',215],['TT-3',435],['TT-2',720],['TT-4',940]]],
        [255,'GATES',[['FG-19',215],['FG-21',435],['FG-20',720],['FG-22',940]]],
        [415,'BUNKER BAYS',[['Unit-1 Coal Bunker Bay',325],['Unit-2 Coal Bunker Bay',830]]]
      ];
      bands.forEach(([y,title,items],idx)=>{
        if(idx>0)decor.push(`<path d="M${frameX+14} ${y-18}H${frameX+frameW-14}" class="ps-floor"/>`);
        decor.push(text(frameX-14,y+40,title,'ps-zone-label','end'));
        items.forEach(([lbl,x])=>putLabel(lbl,x,y,160,74));
      });
      decor.push(`<path d="M${frameX+14} 555H${frameX+frameW-14}" class="ps-floor"/>`,text(frameX-14,620,'MILL BUNKERS','ps-zone-label','end'));
      ['A','B','C','D','E','F'].forEach((let_,i)=>{
        const r=Math.floor(i/3),c=i%3;
        putLabel(`Bunker-${let_} of Unit-1`,185+c*158,572+r*145,134,70);
        putLabel(`Bunker-${let_} of Unit-2`,695+c*158,572+r*145,134,70);
      });
      s.width=1220;s.height=890;s.initialHeight=890;
    }else{
      return null;
    }

    for(const [cid,owner] of chuteOwner){
      if(!positions.has(cid)&&positions.has(owner))positions.set(cid,positions.get(owner));
    }

    const gatewaysSet=new Set(s.nodes.filter(n=>n.kind==='yard').map(n=>n.id));
    const extra=s.nodes.filter(n=>!drawn.has(n.id)&&!chuteOwner.has(n.id)&&!gatewaysSet.has(n.id));
    if(extra.length){
      const base=s.height+30;
      decor.push(text(190,base-12,'ADDITIONAL AREA EQUIPMENT & SERVICES','ps-zone-label','start'));
      extra.forEach((n,i)=>put(n,190+(i%5)*198,base+8+Math.floor(i/5)*152,160,74));
      s.height=base+40+Math.ceil(extra.length/5)*152;
    }

    const continuationFrom=new Map();
    for(const [beltLbl,gateLbl] of [['EAC-4A','KB-FD-3'],['EAC-4B','KB-FD-4'],['EAC-5A','KB-FD-7'],['EAC-5B','KB-FD-8']]){
      const bNode=byLabel.get(beltLbl),gNode=byLabel.get(gateLbl);
      if(bNode&&gNode&&positions.has(gNode.id))continuationFrom.set(bNode.id,positions.get(gNode.id));
    }
    function pv_from(u,v){
      const pu=positions.get(u),pv=positions.get(v);
      if(pu&&pv&&pv.y-pu.y>200&&continuationFrom.has(u))return continuationFrom.get(u);
      return pu;
    }

    const activeEdges=s.edges.filter(a=>{
      const u=a.canonical_subject,v=a.canonical_object;
      if(!positions.has(u)||!positions.has(v)||positions.get(u)===positions.get(v))return false;
      const pu=pv_from(u,v),pv=positions.get(v);
      if(s.area!=='stockyard'&&s.area!=='bunkers'&&(pu.x>=930||pv.x>=930))return false;
      if(pv.y<pu.y-10||pv.y-pu.y>190)return false;
      return true;
    });

    for(const a of activeEdges){
      const f=pv_from(a.canonical_subject,a.canonical_object),t=positions.get(a.canonical_object);
      const k=a.canonical_subject+'>'+a.canonical_object;
      if(t.y>f.y+20&&t.y-f.y<=240){
        const x1=f.x+f.w/2,y1=f.y+f.h+40,x2=t.x+t.w/2,y2=t.y-5;
        routes.set(k,`M${x1} ${y1}C${x1} ${(y1+y2)/2} ${x2} ${(y1+y2)/2} ${x2} ${y2}`);
      }else if(Math.abs(t.y-f.y)<=20&&t.x>f.x){
        const y=f.y+f.h/2;
        routes.set(k,`M${f.x+f.w+10} ${y}L${t.x-10} ${y}`);
      }
    }

    return decor.join('')+edgeMarkup(activeEdges,positions,routes)+[...drawn.values()].map(d=>hotspot(d.n,d.x,d.y,d.w,d.h,{label:d.title,max:d.w<=140?18:24})).join('');
  }
  function areaScene(){
    const structured=structuredAreaScene();
    if(structured)return structured;
    // Fallback for custom/synthetic test graphs
    const graph=PlantExplorerModel.areaGraph(p,s.area),positions=new Map();
    const members=new Map(s.nodes.map(n=>[n.id,n]));
    const gateways=s.nodes.filter(n=>n.kind==='yard');
    const shift=gateways.length?240:0;
    let body=gateways.map((n,i)=>{return `<a class="ps-area-gateway" href="${safe(openURL(n.id))}"><g transform="translate(${60+i*280} 15)"><rect class="ps-halo" x="-10" y="0" width="250" height="205" rx="20"/>${symbol('yard',20,0,185,130)}${text(110,152,n.label,'ps-stage-title')}${text(110,178,'Open yard assembly →','ps-node-hint')}</g></a>`;}).join('');
    graph.nodes.forEach(n=>positions.set(n.id,{x:n.x*1.25+35,y:n.y*1.55+shift+30,w:150,h:100}));
    const routes=new Map();for(const edge of graph.edges){if(edge.bypassLane===undefined)continue;const a=positions.get(edge.from),b=positions.get(edge.to),y=shift+30+(8+edge.bypassLane*12)*1.55,offset=20+edge.bypassLane*3;routes.set(edge.from+'>'+edge.to,`M${a.x+a.w} ${a.y+50}H${a.x+a.w+offset}V${y}H${b.x-offset}V${b.y+50}H${b.x}`);}
    body+=edgeMarkup(s.edges,positions,routes)+graph.nodes.map(n=>{const a=positions.get(n.id);return hotspot(members.get(n.id)||{id:n.id,label:p.entities.get(n.id)?.label,kind:M.kind(p,n.id),role:'equipment'},a.x,a.y,a.w,a.h);}).join('');
    const shown=new Set([...graph.nodes.map(n=>n.id),...gateways.map(n=>n.id)]),extra=s.nodes.filter(n=>!shown.has(n.id));
    const base=graph.height*1.55+shift+90;
    if(extra.length)body+=text(40,base,'OTHER EQUIPMENT IN THIS AREA','ps-zone-label','start')+extra.map((n,i)=>hotspot(n,50+(i%5)*235,base+25+Math.floor(i/5)*200,160,100)).join('');
    s.width=Math.max(1200,graph.width*1.25+120,gateways.length*280+60);s.height=Math.max(720,base+(Math.ceil(extra.length/5))*200+50);return body;
  }
  function inspector(){
    const id=h(),edge=p.facts.find(a=>a.id===q().get('edge'));
    if(edge){const fs=p.networks.filter(a=>a.canonical_subject===edge.canonical_subject&&a.canonical_object===edge.canonical_object&&a.context?.network===edge.context?.network);return `<aside class="ps-inspector" aria-label="Connection details"><a class="ps-close" href="${safe(url({edge:null,pick:null}))}" aria-label="Close details">×</a><div class="ps-eyebrow">DOCUMENTED CONNECTION</div><h2>${safe(p.entities.get(edge.canonical_subject)?.label)} → ${safe(p.entities.get(edge.canonical_object)?.label)}</h2><p>These links retain their individual operating conditions.</p>${(fs.length?fs:[edge]).map(a=>api.fact(a)).join('')}</aside>`;}
    if(!id||!p.entities.has(id))return '';
    const e=p.entities.get(id),own=p.outgoing.get(id)||[],qual=p.qualifications(id),parents=M.closestParents(p,id),located=own.filter(a=>a.predicate==='located_at'),count=M.scene(p,id).nodes.filter(n=>n.role==='part').length;
    const modes=M.modeFacts(own,q().get('opmode'));
    const role=own.find(a=>['equipment_role','purpose','equipment_description','function'].includes(a.predicate));
    const summary=own.filter(a=>!a.canonical_object&&['rated_capacity','design_capacity','motor_rated_power','rated_power','individual_device_count','quantity','model_number','belt_speed','scheduled_nozzle_count','rated_flow'].includes(a.predicate));
    const links=[...(p.incoming.get(id)||[]),...own].filter(a=>a.canonical_object&&!['instance_of','part_of','located_at'].includes(a.predicate));
    return `<aside class="ps-inspector" aria-label="Equipment details"><a class="ps-close" href="${safe(url({pick:null,edge:null}))}" aria-label="Close details">×</a><div class="ps-eyebrow">SELECTED ${safe(nice(M.kind(p,id)))}</div><h2>${safe(e.label)}</h2>${role?`<p class="ps-purpose">${safe(role.value)} ${source(role)}</p>`:`<p>${safe((p.classes.get(id)||[]).map(nice).join(' · '))}</p>`}${id!==s.id?`<a class="ps-open" href="${safe(openURL(id))}">Open ${count?'assembly · '+count+' part'+(count===1?'':'s'):'equipment'} <span>↗</span></a>`:''}${parents.length?`<div class="ps-context-line"><span>Part of</span>${parents.map(x=>`<a href="${safe(openURL(x))}">${safe(p.entities.get(x)?.label)}</a>`).join('')}</div>`:''}${located.length?`<div class="ps-context-line"><span>Located at</span>${located.map(a=>`<a href="${safe(openURL(a.canonical_object))}">${safe(p.entities.get(a.canonical_object)?.label)}</a> ${source(a)}`).join('')}</div>`:''}${qual.length?`<details class="ps-qualified"><summary>${qual.length} source qualifications</summary>${qual.map(x=>api.fact(x.fact,x.via)).join('')}</details>`:''}${summary.length?`<div class="ps-inspector-label">DOCUMENTED VALUES</div>${summary.map(a=>api.fact(a)).join('')}`:''}${modes.modes.length?`<section class="ps-mode-reference"><div class="ps-inspector-label">OPERATING MODE REFERENCE</div><nav aria-label="Documented operating mode">${modes.modes.map(mode=>`<a href="${safe(url({opmode:mode}))}" ${mode===modes.selected?'aria-current="true"':''}>${safe(mode)}</a>`).join('')}</nav><p>Showing source conditions for this mode.</p>${modes.facts.map(a=>api.fact(a)).join('')}</section>`:''}<details class="ps-inspector-section"><summary>General facts & sources <span>${modes.general.length}</span></summary>${modes.general.map(a=>api.fact(a)).join('')}</details>${p.relatedFacts(id).length?`<details class="ps-inspector-section"><summary>Applicable engineering references</summary>${p.relatedFacts(id).map(x=>api.fact(x.fact,x.via)).join('')}</details>`:''}${links.length?`<details class="ps-inspector-section"><summary>Connections & relationships <span>${links.length}</span></summary>${links.map(a=>`<article class="ps-relation"><a href="${safe(openURL(a.canonical_subject===id?a.canonical_object:a.canonical_subject))}">${safe(p.entities.get(a.canonical_subject===id?a.canonical_object:a.canonical_subject)?.label)}</a><p>${safe(nice(a.predicate))} · ${a.canonical_subject===id?'outgoing':'incoming'}</p>${api.fact(a)}</article>`).join('')}</details>`:''}<a class="ps-reference-link" href="${safe(url({equipment:id,view:'records',tab:'assembly',pick:null,edge:null}))}">Search assembly facts & maintenance records →</a></aside>`;
  }
  function browse(){if(!q().has('browse'))return '';const ids=s.all||[...p.entities.keys()].filter(id=>!p.refs.has(id));return `<aside class="ps-browser" aria-label="Component navigator"><a class="ps-close" href="${safe(url({browse:null}))}" aria-label="Close component navigator">×</a><div class="ps-eyebrow">${s.id?'ASSEMBLY NAVIGATOR':'EQUIPMENT NAVIGATOR'}</div><h2>Find a part</h2><input type="search" id="ps-parts-search" aria-label="Filter components" placeholder="Name, tag or type…"><div id="ps-part-results">${ids.map(id=>`<a class="ps-part-row" href="${safe(pickURL(id))}" data-search="${safe([p.entities.get(id)?.label,...p.entities.get(id)?.aliases||[],...p.classes.get(id)||[]].join(' ').toLowerCase())}"><span>${safe(p.entities.get(id)?.label)}</span><small>${safe(nice(M.kind(p,id)))}</small></a>`).join('')}</div></aside>`;}
  function crumbs(){
    const candidates=(q().get('trail')||'').split(',').filter(id=>p.entities.has(id)),trail=[];let child=s.id;
    for(const id of candidates.reverse()){if(id===child||!p.assembly(id).some(n=>n.id===child)&&!(p.incoming.get(id)||[]).some(a=>a.predicate==='located_at'&&a.canonical_subject===child))break;trail.unshift(id);child=id;}
    const chain=trail.length?trail:s.id?M.breadcrumbs(p,s.id).slice(0,-1).filter(id=>!/Maitree Coal Handling Plant|Coal Stockpile Yard/.test(p.entities.get(id)?.label)):[];
    const area=p.stages.find(st=>st.id===q().get('area'))||p.stages.find(st=>p.memberships.get(s.id)?.has(st.id));
    return `<nav class="ps-crumbs" aria-label="Plant location"><a href="${home}">Plant</a>${area?`<span>›</span><a href="${areaURL(area.id)}">${safe(area.short)}</a>`:''}${chain.map((id,i)=>`<span>›</span><a href="${safe(url({equipment:id,trail:chain.slice(0,i).join(','),pick:null,edge:null,browse:null}))}">${safe(p.entities.get(id)?.label)}</a>`).join('')}${s.id?`<span>›</span><strong>${safe(s.title)}</strong>`:''}</nav>`;
  }
  function view(projection,helpers){
    p=projection;api=helpers;const entry=q().get('equipment')||M.areaEntry(p,q().get('area'));s=M.scene(p,entry,q().get('area'));
    const body=s.kind==='plant'?plant():s.kind==='area'?areaScene():q().get('scene')==='connections'?connectionsScene():equipmentScene(),panel=inspector()||browse();
    return `<div class="ps-root ps-scene-${safe(s.kind)} ${['silo-house','extractor','silo','spray-system','crusher-house','crusher','screen','de-house','de-stream','transfer','conveyor','weigher','detector','drive','coupling','pump'].includes(s.kind)?'ps-detail-scene':''}"><header class="ps-top"><a href="#overview" class="ps-brand"><span>CHP</span><div>MAITREE<small>Plant explorer</small></div></a><div class="ps-search"><label class="ps-sr-only" for="ps-search">Find any equipment</label><input id="ps-search" type="search" placeholder="Find equipment, part or tag…" autocomplete="off"><div id="ps-search-results" hidden></div></div><nav class="ps-app-links" aria-label="Workspace"><a href="#desk">Operations desk ↗</a><a href="#documents">Documents</a></nav></header><div class="ps-navigation">${crumbs()}<span class="ps-model">Documented model · v${p.version}</span></div><section class="ps-workspace ${panel?'has-inspector':''}"><div class="ps-main"><header class="ps-heading"><div><div class="ps-eyebrow">${s.kind==='plant'?'THE COAL JOURNEY':s.kind==='area'?'PROCESS AREA':'INSIDE THE PLANT'}</div><h1>${safe(s.title)}</h1><p>${safe(s.description)}</p></div>${s.id?`<a class="ps-details-button" href="${safe(pickURL(s.id))}">About this equipment ⓘ</a>`:''}</header>${contextRail()}${crusherRouteGuide()}${s.kind==='plant'?`<div class="ps-path-guide"><label for="ps-path">Follow a route</label><select id="ps-path"><option value="">Whole plant</option>${p.paths.map(path=>`<option value="${safe(path.id)}" ${path.id===q().get('path')?'selected':''}>${safe(path.title)}</option>`).join('')}</select>${q().get('path')?`<button data-action="scene-path-source" class="ps-source">Route source & conditions ↗</button>`:''}</div>`:''}<div class="ps-toolbar"><div class="ps-layers" aria-label="Connection layers">${[['all','All systems'],['material','Coal flow'],['mechanical','Drive'],['utility','Air, water & oil'],['electrical','Power'],['control','Control']].map(([key,title])=>`<a href="${safe(url({layer:key==='all'?null:key}))}" ${((q().get('layer')||'all')===key)?'aria-current="true"':''}>${title}</a>`).join('')}</div><a class="ps-browse-toggle" href="${safe(url({browse:q().has('browse')?null:'1',pick:null,edge:null}))}">⌕ Find a part</a></div><div class="ps-canvas-wrap"><svg id="ps-canvas" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${s.width||1200} ${s.height||720}" role="group" tabindex="0" aria-label="${safe(s.title)} interactive plant schematic" data-width="${s.width||1200}" data-height="${s.height||720}" data-initial-height="${s.initialHeight||s.height||720}">${defs()}<rect x="-10000" y="-10000" width="25000" height="25000" fill="url(#ps-grid)" opacity=".38"/>${body}</svg><div class="ps-canvas-controls"><button data-action="scene-zoom" data-delta="in" aria-label="Zoom in">+</button><button data-action="scene-zoom" data-delta="out" aria-label="Zoom out">−</button><button data-action="scene-zoom" data-delta="fit">Fit</button>${['conveyor','feeder','yard'].includes(s.kind)&&q().get('scene')!=='connections'?`<a class="ps-spread-toggle" href="${safe(url({spread:q().get('spread')==='1'?null:'1'}))}">${q().get('spread')==='1'?'Assembled':'Spread parts'}</a>`:''}${s.height>760?`<button data-action="scene-zoom" data-delta="all">All parts</button>`:''}<button data-action="scene-motion" aria-pressed="false">▷ Explain flow</button></div><div class="ps-canvas-hint">Select equipment · drag to pan · + / − to zoom</div></div><div class="ps-legend"><span><i class="ps-key material"></i>Coal</span><span><i class="ps-key mechanical"></i>Mechanical drive</span><span><i class="ps-key utility"></i>Air / water / oil</span><span><i class="ps-key electrical"></i>Electrical supply</span><span><i class="ps-key control"></i>Control</span><span><i class="ps-key attachment"></i>Assembly attachment</span><span class="ps-basis">Illustrative arrangement · no live status</span></div>${s.kind!=='plant'?`<nav class="ps-plant-strip" aria-label="Plant context">${p.stages.map(st=>`<a href="${areaURL(st.id)}" ${p.memberships.get(s.id)?.has(st.id)||s.area===st.id?'aria-current="true"':''}><span>${String(st.number).padStart(2,'0')}</span>${safe(st.short)}</a>`).join('')}</nav>`:''}</div>${panel}</section></div>`;
  }
  function bind(){
    cleanup?.();const root=document.querySelector('.ps-root');document.body.classList.toggle('ps-mode',!!root);if(!root)return;
    const svg=document.getElementById('ps-canvas'),input=document.getElementById('ps-search'),results=document.getElementById('ps-search-results');
    input.oninput=()=>{const words=input.value.trim().toLowerCase().split(/\s+/).filter(Boolean);results.hidden=!words.length;const rows=[...p.entities.values()].filter(e=>words.every(w=>[e.label,...e.aliases||[]].join(' ').toLowerCase().includes(w))).sort((a,b)=>Number(b.label.toLowerCase()===input.value.trim().toLowerCase())-Number(a.label.toLowerCase()===input.value.trim().toLowerCase()));results.innerHTML=rows.slice(0,30).map(e=>`<a href="${safe(openURL(e.id))}"><strong>${safe(e.label)}</strong><small>${safe(nice(M.kind(p,e.id)))}</small></a>`).join('')||'<p>No matching equipment.</p>';};
    input.onkeydown=e=>{if(e.key==='Escape')results.hidden=true;};
    const filter=document.getElementById('ps-parts-search');if(filter)filter.oninput=()=>document.querySelectorAll('.ps-part-row').forEach(el=>el.hidden=!el.dataset.search.includes(filter.value.toLowerCase()));
    const key=[s.id,s.area,s.kind,q().get('scene')].join('|');
    const fit=(all=false)=>{viewport={x:0,y:0,w:Number(svg.dataset.width),h:Number(all?svg.dataset.height:svg.dataset.initialHeight)};apply();};
    const apply=()=>svg.setAttribute('viewBox',`${viewport.x} ${viewport.y} ${viewport.w} ${viewport.h}`);
    if(key!==viewKey){viewKey=key;fit();}else apply();
    root._zoom=direction=>{if(direction==='fit'||direction==='all'){fit(direction==='all');return;}const scale=direction==='in'?.8:1.25;if(viewport.w*scale<220||viewport.w*scale>12000)return;viewport.x+=viewport.w*(1-scale)/2;viewport.y+=viewport.h*(1-scale)/2;viewport.w*=scale;viewport.h*=scale;apply();};
    let drag=null,moved=false;
    svg.onpointerdown=e=>{if(e.button!==0||e.target.closest('[data-action],a'))return;drag={x:e.clientX,y:e.clientY,v:{...viewport}};moved=false;svg.setPointerCapture(e.pointerId);};
    svg.onpointermove=e=>{if(!drag)return;const r=svg.getBoundingClientRect(),scale=Math.max(viewport.w/r.width,viewport.h/r.height);viewport.x=drag.v.x-(e.clientX-drag.x)*scale;viewport.y=drag.v.y-(e.clientY-drag.y)*scale;moved=true;apply();};
    svg.onpointerup=()=>drag=null;svg.onpointercancel=()=>drag=null;
    svg.onkeydown=e=>{if(e.target!==svg)return;if(['+','=','-','0','ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key)){e.preventDefault();if(['+','=','-','0'].includes(e.key))root._zoom(e.key==='0'?'fit':e.key==='-'?'out':'in');else{viewport.x+=e.key==='ArrowLeft'?-50:e.key==='ArrowRight'?50:0;viewport.y+=e.key==='ArrowUp'?-50:e.key==='ArrowDown'?50:0;apply();}}};
    const pathSelect=document.getElementById('ps-path');if(pathSelect)pathSelect.onchange=()=>location.hash=url({path:pathSelect.value||null});
    const close=e=>{if(e.key==='Escape'&&!document.getElementById('dialog')?.open){if(h()||q().has('edge')||q().has('browse'))location.hash=url({pick:null,edge:null,browse:null});}};document.addEventListener('keydown',close);cleanup=()=>document.removeEventListener('keydown',close);
    const selected=h()||q().get('edge')||(q().has('browse')?'browse':'');
    if(selected!==lastPick){lastPick=selected;if(selected)requestAnimationFrame(()=>{const panel=document.querySelector('.ps-inspector,.ps-browser'),heading=panel?.querySelector('h2');heading?.setAttribute('tabindex','-1');heading?.focus({preventScroll:true});if(window.matchMedia('(max-width:760px)').matches)panel?.scrollIntoView({block:'start',behavior:window.matchMedia('(prefers-reduced-motion:reduce)').matches?'instant':'smooth'});});}
  }
  async function action(name,el){
    if(!name.startsWith('scene-'))return false;
    if(name==='scene-pick')location.hash=pickURL(el.dataset.id);
    if(name==='scene-path-source'){const path=p.paths.find(x=>x.id===q().get('path'));if(path)modal('Documented route',path.facts.map(a=>api.fact(a)).join(''));}
    if(name==='scene-edge')location.hash=url({edge:el.dataset.id,pick:null,browse:null});
    if(name==='scene-zoom')document.querySelector('.ps-root')?._zoom(el.dataset.delta);
    if(name==='scene-motion'){const active=document.getElementById('ps-canvas')?.classList.toggle('ps-explain');el.setAttribute('aria-pressed',String(!!active));el.textContent=active?'Ⅱ Stop illustration':'▷ Explain flow';const hint=document.querySelector('.ps-canvas-hint');if(hint)hint.textContent=active?'Illustrating documented directions · alternatives may not run together':'Select equipment · drag to pan · + / − to zoom';}
    return true;
  }
  return {view,bind,action};
})();