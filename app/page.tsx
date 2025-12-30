import NavbarHome from "./components/navbar";
import Prism from "./components/prisim";

const Home = () => {

  console.log("what type of file is this");

  return (
    <main>
      <div style={{ width: '100%', height: '100%', position: 'absolute', zIndex: -1 }}>
        <Prism
          animationType="rotate"
          timeScale={0.5}
          height={3.5}
          baseWidth={5.5}
          scale={3.6}
          hueShift={0}
          colorFrequency={1}
          noise={0.5}
          glow={1}
        />
      </div>
      <NavbarHome />
      <div>welcome to nextjs</div>
    </main>
  ) 
}

export default Home