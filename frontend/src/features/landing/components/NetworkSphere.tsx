const nodes = Array.from({ length: 48 }, (_, index) => {
  const angle = index * 2.399963;
  const radius = 55 + (index % 6) * 5;
  return { x: 100 + Math.cos(angle) * radius, y: 100 + Math.sin(angle) * radius * 0.76, r: index % 9 === 0 ? 2.6 : 1.25 };
});
const edges = nodes.flatMap((node, index) => [1, 5].filter((step) => index + step < nodes.length).map((step) => ({ from: node, to: nodes[index + step], id: `${index}-${step}` })));

export function NetworkSphere({ small = false }: { small?: boolean }) {
  return <div className={`network-sphere ${small ? 'network-sphere-small' : ''}`} aria-hidden="true">
    <div className="sphere-tilt"><svg viewBox="0 0 200 200" className="sphere-svg"><ellipse cx="100" cy="100" rx="82" ry="66" className="sphere-ring" />{edges.map(({ from, to, id }) => <line key={id} x1={from.x} y1={from.y} x2={to.x} y2={to.y} className="sphere-edge" />)}{nodes.map((node, index) => <circle key={index} cx={node.x} cy={node.y} r={node.r} className={`sphere-node ${index % 7 === 0 ? 'sphere-node-major' : ''}`} />)}</svg></div><span className="sphere-particle particle-one" /><span className="sphere-particle particle-two" /><span className="sphere-particle particle-three" /></div>;
}
