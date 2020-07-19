import 'react-native-gesture-handler';
import React, { useState } from 'react';
import {NavigationContainer, useNavigation} from '@react-navigation/native';
import { StyleSheet, Text, View, Image, TextInput, TouchableOpacity, SafeAreaView, SectionList, Linking} from 'react-native';
import { createStackNavigator } from '@react-navigation/stack';
import {CheckBox} from 'react-native-elements';
import vt from './assets/vote_top.png';
import { Stitch, UserPasswordAuthProviderClient,UserPasswordCredential, RemoteMongoClient} from "mongodb-stitch-react-native-sdk";
import {Formik} from 'formik';
import { render } from 'react-dom';

Stitch.initializeDefaultAppClient('e-vote-uzpct');



function LogIn(){
  const [email, setEmail] = useState('');
  const [passWord, setpassWord] = useState('');
  const navigation = useNavigation();
  function op(){
    const app = Stitch.defaultAppClient
    const credential = new UserPasswordCredential(email, passWord)
    app.auth.loginWithCredential(credential)
    // Returns a promise that resolves to the authenticated user
    .then(authedUser => navigation.navigate('entered'))
    .catch(err => alert("Login failed: " + err))
  }

  function nu(){
    const emailPasswordClient = Stitch.defaultAppClient.auth.getProviderClient(UserPasswordAuthProviderClient.factory);
    emailPasswordClient.registerWithEmail(email, passWord).then(() => navigation.navigate('entered')).catch(err =>alert("Error registering new user: " + err));
  }

  return(
    <View style = {{flex: 1, alignItems: 'center'}}>
      <TextInput style = {styles.text_user} textAlign = {'center'}
      placeholder = "Email"
      onChangeText = {(em) => setEmail(em)}
      />
      <TextInput style = {styles.text_pass} textAlign = {'center'}
      placeholder = "Password"
      onChangeText = {(pass) => setpassWord(pass)}
      />

      <TouchableOpacity onPress = {op} style = {styles.log_but}><Text style = {styles.but_text}> Log In</Text></TouchableOpacity> 
      <TouchableOpacity onPress = {nu} style = {styles.ca_but}><Text style = {styles.but_text}> Create Account</Text></TouchableOpacity> 
    </View>
  )
}

function li_screen(){
  return(
    <View style={styles.container}>
      <Image source = {vt} style = {styles.vote_top} />
      <Text style = {styles.text_intro}>Welcome to eLector, your online voting platform!</Text>
      <LogIn />
    </View>
  )
}

var cit = [];
function cl_show(data_arr, url_arr, type){
  cit = [];

  const Item = function ({titl}) {
    const [check, setcheck] = useState(false);

    function op(){
      setcheck(!check);
      if(!check){
        cit.push(titl);
      }
      else{
        let ind = cit.indexOf(titl)
        if(ind > -1){
          cit.splice(ind,1)
        }
      }
    }

    return(
    <View>
      <CheckBox   title = {titl} checked = {check} onPress={op} onLongPress ={() => Linking.openURL(((url_arr[0]).url)[0])} />
    </View>)
  }; 

  function upd(){
    for(let i = 0; i< cit.length;i++){
      cit[i] = cit[i].slice(0,cit[i].indexOf("(")-1);
    }

    const gd=  Stitch.defaultAppClient;
    const mdb = gd.getServiceClient(RemoteMongoClient.factory, "mongodb-atlas");
    let ncol = "hey";
    if(type == "nat"){
      ncol = mdb.db("candidates").collection("national_candidates");
    }
    else if(type == "stat"){
      ncol = mdb.db("candidates").collection("state_candidates");
    }
    else if(type == "loc"){
      ncol = mdb.db("candidates").collection("local_candidates");
    }
    else{
      alert("Error!");
    }


    for(let i = 0; i< cit.length;i++){
      const query = {"name": cit[i]};
      const update = {"$inc": {"count": 1}}
      ncol.updateOne(query, update);
    }

  }

  return(
    <SafeAreaView style={styles.container3}>
      <View style = {{flex: 3}}>
        <SectionList  
        sections = {data_arr}
        keyExtractor = {(item, index) => item + index}
        renderItem={function ({ item }) {return(<Item titl={item} />)}}
        renderSectionHeader={function ({ section: { titl } }) { return((
          <Text style = {styles.head_style} >{titl}</Text>
        ))}}
        />
      </View>

      <View style = {{flex: 1}}><TouchableOpacity onPress = {upd} style = {styles.sub_page_but}><Text style = {styles.but_text}> Submit</Text></TouchableOpacity></View>
      
    </SafeAreaView>
  ) 

}

class nat_screen extends React.Component{
  constructor(props){
    super(props);
    this.state = {
      dat: [],
      urls: []
    };
    this._get_data = this._get_data.bind(this);
  }

  componentDidMount(){
    this._get_data();
  }

  _get_data(){
    const gd=  Stitch.defaultAppClient;
    const mdb = gd.getServiceClient(RemoteMongoClient.factory, "mongodb-atlas");
    const ncol = mdb.db("candidates").collection("national_candidates");
    ncol.find().toArray().then(data  =>{
        data.forEach((item)  => {
          let tempdat = this.state.dat.slice();
          let tempurl = this.state.urls.slice();
          let added = 0;
          for(let i = 0; i < this.state.dat.length; i++){
            if(this.state.dat[i]["titl"] == item["category"]){
              tempdat[i]["data"].push(item["name"] + " (" + item["party"] + ")");
              added = 1;
            }
          }
            
          for(let i = 0; i < this.state.urls.length; i++){
            if(this.state.urls[i]["titl"] == item["category"]){
              tempurl[i]["url"].push(item["url"]);
            }
          }
          
          if(added == 0){
            tempdat.push({titl: item["category"], data: [item["name"] + " (" + item["party"] + ")"]});
            tempurl.push({titl: item["category"], url: [item["url"]]});
          }
      
          this.setState({dat: tempdat});
          this.setState({urls: tempurl});
        })
      }
    )
  } 

  /* Harcoded Test Data
  const dat = [{titl: "President of the United States", data: ["Barack Obama (Democrat)", "Mitt Romney (Republican)", "Gary Johnson (Libertarian)", "Jill Stein (Green)" ]}, 
  {titl: "Senator From the State of Texas", data: ["Beto O'Rourke (Democrat)", "Ted Cruz (Republican)" ]}];

  const urls = [{titl: "President of the United States", url: ["https://en.wikipedia.org/wiki/Barack_Obama_2012_presidential_campaign", "https://en.wikipedia.org/wiki/Mitt_Romney_2012_presidential_campaign"]}]
  */

  render(){
    return cl_show(this.state.dat, this.state.urls, "nat");
  }

} 

class stat_screen extends React.Component{
  constructor(props){
    super(props);
    this.state = {
      dat: [],
      urls: []
    };
    this._get_data = this._get_data.bind(this);
  }


  componentDidMount(){
    this._get_data();
  }


  _get_data(){
    const gd=  Stitch.defaultAppClient;
    const mdb = gd.getServiceClient(RemoteMongoClient.factory, "mongodb-atlas");
    const ncol = mdb.db("candidates").collection("state_candidates");
    ncol.find().toArray().then(data  =>{
        data.forEach((item)  => {
          let tempdat = this.state.dat.slice();
          let tempurl = this.state.urls.slice();
          let added = 0;
          for(let i = 0; i < this.state.dat.length; i++){
            if(this.state.dat[i]["titl"] == item["category"]){
              tempdat[i]["data"].push(item["name"] + " (" + item["party"] + ")");
              added = 1;
            }
          }
            
          for(let i = 0; i < this.state.urls.length; i++){
            if(this.state.urls[i]["titl"] == item["category"]){
              tempurl[i]["url"].push(item["url"]);
            }
          }
          
          if(added == 0){
            tempdat.push({titl: item["category"], data: [item["name"] + " (" + item["party"] + ")"]});
            tempurl.push({titl: item["category"], url: [item["url"]]});
          }
      
          this.setState({dat: tempdat});
          this.setState({urls: tempurl});
        })
      }
    )
  } 

  render(){
    return cl_show(this.state.dat, this.state.urls, "stat");
  }

} 

class loc_screen extends React.Component{
  constructor(props){
    super(props);
    this.state = {
      dat: [],
      urls: []
    };
    this._get_data = this._get_data.bind(this);
  }


  componentDidMount(){
    this._get_data();
  }

  _get_data(){
    const gd=  Stitch.defaultAppClient;
    const mdb = gd.getServiceClient(RemoteMongoClient.factory, "mongodb-atlas");
    const ncol = mdb.db("candidates").collection("local_candidates");
    ncol.find().toArray().then(data  =>{
        data.forEach((item)  => {
          let tempdat = this.state.dat.slice();
          let tempurl = this.state.urls.slice();
          let added = 0;
          for(let i = 0; i < this.state.dat.length; i++){
            if(this.state.dat[i]["titl"] == item["category"]){
              tempdat[i]["data"].push(item["name"] + " (" + item["party"] + ")");
              added = 1;
            }
          }
            
          for(let i = 0; i < this.state.urls.length; i++){
            if(this.state.urls[i]["titl"] == item["category"]){
              tempurl[i]["url"].push(item["url"]);
            }
          }
          
          if(added == 0){
            tempdat.push({titl: item["category"], data: [item["name"] + " (" + item["party"] + ")"]});
            tempurl.push({titl: item["category"], url: [item["url"]]});
          }
      
          this.setState({dat: tempdat});
          this.setState({urls: tempurl});
        })
      }
    )
  } 

  render(){
    return cl_show(this.state.dat, this.state.urls, "loc");
  }

} 



function enter_screen(){
  const navigation = useNavigation();

  function ne(){
    navigation.navigate('national');
  }

  function st(){
    navigation.navigate('state');
  }

  function loc(){
    navigation.navigate('local');
  }

  return(
    <View style = {styles.container2}>
      <View style ={{flex:1}}><Text style = {styles.top_tex}>Congratulations, you are logged in and ready to submit your ballot!</Text></View>
      <View style ={{flex:1}}><TouchableOpacity onPress ={ne} style = {styles.ne_but}><Text style = {styles.nelsele_but_text}>National Elections</Text></TouchableOpacity></View>
      <View style ={{flex:1}}><TouchableOpacity onPress = {st} style = {styles.se_but}><Text style = {styles.nelsele_but_text}>State Elections</Text></TouchableOpacity></View>
      <View style ={{flex:1}}><TouchableOpacity onPress = {loc} style = {styles.le_but}><Text style = {styles.nelsele_but_text}>Local Elections</Text></TouchableOpacity></View>
      <View style ={{flex:1}}><TouchableOpacity style = {styles.sub_but}><Text style = {styles.nelsele_but_text}>Submit Ballot</Text></TouchableOpacity></View>
    </View>
  )
}

export default function App() {

  const Stack = createStackNavigator();
  return (
    <NavigationContainer>
      <Stack.Navigator>
        <Stack.Screen  name = "login" component = {li_screen} options={{ title: 'Log In' }}/>
        <Stack.Screen name = "entered" component = {enter_screen} options={{ title: 'Welcome!' }} />
        <Stack.Screen name = "national" component = {nat_screen} options={{ title: 'National Elections' }} />
        <Stack.Screen name = "state" component = {stat_screen} options={{ title: 'State Elections' }} />
        <Stack.Screen name = "local" component = {loc_screen} options={{ title: 'Local Elections' }} />
      </Stack.Navigator>
    </NavigationContainer>

  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
  },
  container2: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'space-between'
  },
  container3: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
  },
  vote_top: {
    width: 400,
    height: 200,
    top: 50
  },
  text_intro:{
    fontSize: 25,
    fontWeight: "bold",
    justifyContent: 'center',
    textAlign: 'center',
    top: 80
  },
  text_user: {
    width: 400,
    borderWidth: 2, 
    fontSize: 40,
    top: 120
  },
  text_pass: {
    width: 400,
    borderWidth: 2, 
    fontSize: 40,
    top: 150
    
  },
  log_but: {
    top: 180,
    width:130,
    height: 40,
    alignItems: 'center',
    backgroundColor: 'blue'
  },
  ca_but: {
    top: 220,
    width: 250,
    height: 40,
    alignItems: 'center',
    backgroundColor: 'blue'
  },
  but_text: {
    fontSize: 30,
    color: 'white'
  },
  head_style: {
    color: 'black',
    fontWeight: 'bold',
    fontStyle: 'italic',
    fontSize: 20,
    textAlign: 'left'
  },
  top_tex: {
    textAlign: 'center',
    fontSize: 25,
    top: 20,
    width: 400
  },
  ne_but: {
    height: 60,
    width: 300,
    backgroundColor:'red',
    alignItems: 'center',
    justifyContent: 'center'
  },
  se_but: {
    height: 60,
    width: 300,
    backgroundColor:'gray',
    alignItems: 'center',
    justifyContent: 'center'
  },
  le_but: {
    height: 60,
    width: 300,
    backgroundColor:'blue',
    alignItems: 'center',
    justifyContent: 'center'
  },
  sub_but: {
    height: 60,
    width: 300,
    backgroundColor: 'black',
    alignItems: 'center',
    justifyContent: 'center'
  },
  sub_page_but: {
    height: 50,
    width: 200,
    backgroundColor: 'black',
    alignItems: 'center',
    justifyContent: 'center'
  },
  nelsele_but_text: {
    fontSize: 25,
    color: 'white',
    fontWeight: 'bold'
  }
});
