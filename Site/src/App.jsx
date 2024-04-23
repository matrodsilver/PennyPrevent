import Navbar from "./components/Navbar/Navbar";


function App() {
  return (
    <div>
      <Navbar />
      <div className="container mx-auto py-8">
        <h1 className="dark:text-gray-200 text-3xl font-bold mb-4">Análise de dados com Iot</h1>
        <div className="text-lg  container mx-auto font-bold ">Chatbot</div>
        <div style={{ height: '3px', width: '70px' }} className="bg-reply-100 mb-4"></div>
        <div style={{ height: '600px', width: '100%' }} className="bg-gray-300 rounded-t border-2 border-black shadow-xl text-black" ></div>
        <div style={{ height: '50px', width: '100%' }} className=" rounded-b  border-2 border-black border-t-0 bg-gray-500 text-gray-400 p-3 shadow-xl">Escreva sua mensagem aqui...</div>
        <p className="dark:text-gray-200 text-lg font-bold mt-20">Dashboard</p>
        <div style={{ height: '3px', width: '93px' }} className="bg-reply-100 mb-4"></div>
        <div style={{ height: '650px', width: '100%' }} className="bg-gray-300 rounded-md border-2 shadow-xl border-black dark:border-blue shadow-xl"></div>
      </div>
    </div>
  );
}

export default App;