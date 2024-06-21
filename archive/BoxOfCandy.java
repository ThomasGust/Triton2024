public class BoxOfCandy{

    private Candy[][] box;
    
    public boolean moveCandyToFirstRow(int col){
        for (int i =0; i<box.length; i++){
            if (box[i][col] != null){
                for (int k = 0; k<box[0].length; k++){
                    if (box[0][k]==null){
                        box[0][k] = box[i][col];
                        box[i][col] = null;
                        return true;
                    }
                }
            }
        }
        return false;
    }

    public Candy removeNextByFlavor(String flavor){
        for (int i==0; i<box.length; i++){
            for (int j ==0; j<box[0].length; j++){
                if (box[i][j].getFlavor().equals(flavor)){
                    Candy toremove = box[i][j];
                    box[i][j] = null;
                    return toremove
                }
            }
        }
    }
}

public class WeatherData{

    private ArrayList<Double> temperatures;

    public void cleanData(double lower, double upper){
        for (int i = 0; i<temperatures.length; i++){
            if (temperatures.get(i)<lower || temperatures.get(i)>upper){
                temperatures.remove(i);
                i--;
            }
        }
    }
    public int longestHeatWave(double threshold){
        int longest = 0;
        int current = 0;

        for (int i=0; i<temperatures.length; i++){
            if (temperatures.get(i)>threshold){
                current++;}
            else{
                if (current > longest){
                    longest = current;
                }
                current = 0;
            }
            }
        return longest;
        }
    }

public class ApointmentBook{

    private boolean isMinuteFree(int period, int minute){

    }

    private boolean reserveBlock(int period, int startMinute, int duration){

    }

    public int findFreeBlock(int period, int duration){
        for (int i = 0; i<60-duration; i++){
            if (isMinuteFree(period, i)){
                int j = i;
                while (j<60 && isMinuteFree(period, j)){
                    j++;
                }
                if (j-i>=duration){
                    return i;
                }
            }
        }
        return -1;
    }

    public boolean makeAppointment(int startPeriod, int endPeriod, int duration){
        for (int i = startPeriod; i<endPeriod; i++){
            if (findFreeBlock(i, duration) >= 0){
                return reserveBlock(endPeriod, i, duration);
            }
        }
        return false;
    }
}

public class Sign{
    String str;
    int x;

    public Sign(String str, int x){
        this.str = str;
        this.x = x;
    }

    public int numberOfLines(){
        int le = str.length();
        double lines = Math.ceil((double)le/x);
    }

    public String getLines(){
        String[] lines = new String[(int)numberOfLines()];
        for (int i = 0; i<lines.length; i++){
            lines[i] = str.substring(i*x, Math.min((i+1)*x, str.length()));
        }
        String ret;
        for (int i = 0; i<lines.length; i++){
            ret += lines[i].toString() + ";"; 
        }
        return ret.substring(0, ret.length()-1);
    }
}

public class WeatherData{
    public static void main
}